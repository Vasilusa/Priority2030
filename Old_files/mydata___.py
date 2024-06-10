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
    DATASET_DIR = '../data'
    CACHE_DIR = '../cache'
    mystem = Mystem()

    def __init__(self, data_dir, cache_dir):
        self.DATASET_DIR = data_dir
        self.CACHE_DIR = cache_dir

    def extract_text_and_labels(self, dataframe, text_field_name, label_field_name):
        text_df = dataframe[text_field_name]
        label_df = dataframe[label_field_name]
        # if lemmatize:
        #     text_df = text_df.map(self.lemmatize)
        # if categorical:
        #     label_df = tf.keras.utils.to_categorical(label_df)
        return text_df, tf.keras.utils.to_categorical(label_df)

    @staticmethod
    def to_dataset(text_array, label_array):
        return tf.data.Dataset.from_tensor_slices((text_array, label_array))

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
        ds = Data.to_dataset(all_texts, all_labels).shuffle(len(all_texts))
        train_ds, other_ds = Data.split(ds, 0.8)
        validation_ds, test_ds = Data.split(other_ds, 0.5)

        return train_ds, validation_ds, test_ds


    def get_kinopoisk_data(self):
        dir = self.DATASET_DIR + '/kinopoisk-sentiment-classification/'
        train_df = pd.read_json(dir + 'train.jsonl', lines=True)
        validation_df = pd.read_json(dir + 'validation.jsonl', lines=True)
        test_df = pd.read_json(dir + 'test.jsonl', lines=True)
        train_ds = self.to_dataset(*self.extract_text_and_labels(train_df, 'text', 'label'))
        validation_ds = self.to_dataset(*self.extract_text_and_labels(validation_df, 'text', 'label'))
        test_ds = self.to_dataset(*self.extract_text_and_labels(test_df, 'text', 'label'))

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
        train_text_df, train_label_df = self.extract_text_and_labels(train_df, 'text', 'sentiment')
        train_ds = to_dataset(train_df)
        validation_ds = to_dataset(validation_df)
        validation_ds, test_ds = Data.split(validation_ds, 0.5)

        return train_ds, validation_ds, test_ds


    def get_tabiturient_data(self):
        df = pd.read_json(self.DATASET_DIR + '/tabiturient/all-reviews.jsonl', lines=True)
        # other_df = df[df['parent_url'] != 'https://tabiturient.ru/vuzu/mgtu']
        # test_df = df[df['parent_url'] == 'https://tabiturient.ru/vuzu/mgtu']
        text_df, label_df = self.extract_text_and_labels(df, 'content', 'label')
        ds = self.to_dataset(text_df, label_df).shuffle(len(df))
        train_ds, other_ds = Data.split(ds.shuffle(len(ds)), 0.8)
        test_ds, validation_ds = Data.split(other_ds, 0.5)

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

    # def lemmatize_dataset(self, dataset):
    #     dataset.map(lambda text, label: (self.lemmatize(text), label))

    def vectorize(self, dataset, vectorize_layer):
        return dataset.map(lambda text, label: (vectorize_layer(text), label))

    def adapt(self, dataset, vectorize_layer):
        vectorize_layer.adapt(dataset.map(lambda text, label: text))

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