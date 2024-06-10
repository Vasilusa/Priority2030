import sys

import numpy as np
import os
import tensorflow as tf

#import mydata

import pymystem3

mystem = pymystem3.Mystem()

S = "Это случилось летом в час небывало жаркого заката"

print(mystem.lemmatize(S))

print(mystem.analyze(S))

# data = mydata.Data('/home/alex/Data/datasets', 'cache')
#
# train, val, test = data.get_kinopoisk_data()



# data.save('tabiturient', train_ds, val_ds, test_ds)

#r1 = data.lemmatize('Я пришел домой после фильма')

# ds = tf.data.Dataset.from_tensor_slices((['я ненавижу этого человека', 'идем под пиратским флагом'], [0,1]))
#
# ds2 = data.lemmatize_dataset(ds)

# ds.map(lambda x, y: x)

# for el in train.take(2):
#     print(el)


# t = tf.constant(['A', 'B', 'C'])
# t2 = tf.constant(['D', 'E', 'F'])
#
# print(t+t2)
#
# print(t)
#
# ds = mydata.get_dataset(tf.constant(['A', 'B', 'C']), tf.constant([1, 2, 3]), 'test')
#
# for el in ds:
#     print(el)

# def f(n):
#     return n+1
#
# a = np.array(['я ненавижу этого человека', 'идем под пиратским флагом'])
# r = mydata.mystem.lemmatize(a)
# print(r)



