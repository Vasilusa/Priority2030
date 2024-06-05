import pandas as pd
from pymystem3 import Mystem
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

LABELS = {
    'Bad':0,
    'Neutral':1,
    'Good':2,
}

class Data:
    CACHE_DIR = 'cache'
    def __init__(self, cache_dir):
        self.CACHE_DIR = cache_dir
        self.mystem = Mystem()

    def save(self, name, train_ds, validation_ds, test_ds):
        train_ds.save(self.CACHE_DIR + '/' + name + '/train')
        validation_ds.save(self.CACHE_DIR + '/' + name + '/validation')
        test_ds.save(self.CACHE_DIR + '/' + name + '/test')

    def load(self, name):
        return (
            tf.data.Dataset.load(self.CACHE_DIR + '/' + name + '/train'),
            tf.data.Dataset.load(self.CACHE_DIR + '/' + name + '/validation'),
            tf.data.Dataset.load(self.CACHE_DIR + '/' + name + '/test'),
        )


    def lemmatize(self, text):
        parts = self.mystem.lemmatize(text)
        return "".join(parts)

    def vectorize(self, dataset, vectorize_layer):
        return dataset.map(lambda text, label: (vectorize_layer(text), label))

    def get_text_only_dataset(self, dataset):
        dataset.map(lambda text, label: text)

    @staticmethod
    def split(ds, val):
        count = int(val * len(ds))
        return ds.take(count), ds.skip(count)

    def plot(self, history):
        history_dict = history.history
        loss_values = history_dict["loss"]
        val_loss_values = history_dict["val_loss"]
        accuracy_values = history_dict["accuracy"]
        val_accuracy_values = history_dict["val_accuracy"]
        epochs = range(1, len(loss_values) + 1)
        plt.plot(epochs, loss_values, "bo", label="Потери на этапе обучения")
        plt.plot(epochs, val_loss_values, "ro", label="Потери на этапе проверки")
        plt.plot(epochs, accuracy_values, "b", label="Точность на этапе обучения")
        plt.plot(epochs, val_accuracy_values, "r", label="Точность на этапе проверки")
        plt.title("Потери и точность на этапах обучения и проверки")
        plt.xlabel("Эпохи")
        plt.ylabel("Потери")
        plt.legend()
        plt.show()