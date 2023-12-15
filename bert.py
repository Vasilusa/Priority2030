import os
import keras
import keras_nlp

os.environ["KERAS_BACKEND"] = "tensorflow"


class Classifier:
    def __init__(self):
        self.classifier = keras.saving.load_model("bert_tiny_imdb.dat")

    def get_model(self):
        return "bert_tiny_en_uncased_imdb"

    def get_version(self):
        return 1

    def apply(self, messages_block):
        return self.classifier.predict(messages_block)
