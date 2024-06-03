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
    DATASET_DIR = 'data'
    CACHE_DIR = 'cache'
    mystem = Mystem()

    def __init__(self, data_dir, cache_dir):
        self.DATASET_DIR = data_dir
        self.CACHE_DIR = cache_dir

    def get_twitter_data(self):
        url = self.DATASET_DIR + '/RuTweetCorp/'
        pos_df = pd.read_csv(url + "positive.csv")
        neg_df = pd.read_csv(url + "negative.csv")
        pos_labels = np.empty(len(pos_df))
        neg_labels = np.empty(len(neg_df))
        pos_labels.fill(1)
        neg_labels.fill(0)
        pos_texts = self.lemmatize(np.array(pos_df['ttext']))
        neg_texts = self.lemmatize(np.array(neg_df['ttext']))
        all_texts = np.concatenate((pos_texts, neg_texts), axis=0)
        all_labels = np.concatenate((pos_labels, neg_labels), axis=0)
        ds = tf.data.Dataset.from_tensor_slices((all_texts, all_labels)).shuffle(len(all_texts))
        train_ds, other_ds = Data.split(ds, 0.8)
        validation_ds, test_ds = Data.split(other_ds, 0.5)

        return train_ds, validation_ds, test_ds


    def get_kinopoisk_data(self):
        def to_dataset(dataframe):
            return tf.data.Dataset.from_tensor_slices((
                self.lemmatize(dataframe['text']),
                tf.keras.utils.to_categorical(dataframe['label'])
            ))

        dir = self.DATASET_DIR + '/kinopoisk-sentiment-classification/'
        train_df = pd.read_json(dir + 'train.jsonl', lines=True)
        validation_df = pd.read_json(dir + 'validation.jsonl', lines=True)
        test_df = pd.read_json(dir + 'test.jsonl', lines=True)
        train_ds = to_dataset(train_df)
        validation_ds = to_dataset(validation_df)
        test_ds = to_dataset(test_df)

        return train_ds, validation_ds, test_ds


    def get_ru_sentiment_data(self):
        SPECIFIC_LABELS = {
            0: 'Neutral',
            2: 'Bad',
            1: 'Good',
        }

        def to_dataset(dataframe):
            return tf.data.Dataset.from_tensor_slices((
                self.lemmatize(dataframe['text']),
                tf.keras.utils.to_categorical(dataframe['sentiment'].map(adjust_labels))
            ))

        def adjust_labels(specific_label):
            return LABELS[SPECIFIC_LABELS[specific_label]]

        dir = self.DATASET_DIR + '/RuSentiment/'
        train_df = pd.read_csv(dir + 'train.csv')
        validation_df = pd.read_csv(dir + 'valid.csv')

        train_ds = to_dataset(train_df)
        validation_ds = to_dataset(validation_df)
        validation_ds, test_ds = Data.split(validation_ds, 0.5)

        return train_ds, validation_ds, test_ds



    def get_tabiturient_data(self):
        def to_dataset(dataframe):
            return tf.data.Dataset.from_tensor_slices((
                dataframe['content'].map(self.lemmatize),
                tf.keras.utils.to_categorical(dataframe['label'])
            ))
        df = pd.read_json(self.DATASET_DIR + '/tabiturient/all-reviews.jsonl', lines=True)
        other_df = df[df['parent_url'] != 'https://tabiturient.ru/vuzu/mgtu']
        test_df = df[df['parent_url'] == 'https://tabiturient.ru/vuzu/mgtu']
        other_ds = to_dataset(other_df)
        test_ds = to_dataset(test_df)
        train_ds, validation_ds = Data.split(other_ds.shuffle(len(other_ds)), 0.9)

        return train_ds, validation_ds, test_ds

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

    def adapt(self, dataset, vectorize_layer):
        vectorize_layer.adapt(dataset.map(lambda text, label: text))


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