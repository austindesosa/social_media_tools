# -*- coding: utf-8 -*-
"""test_by_color.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1U8Fjmp_bVJKDoCOvxqOJy2cneSZuSHKH

The following is meant to test neural networks for their ability to distinguish colors. THe purpose is to quickly train and test tensorflow.keras.Model objects without using any external datasets or files. It uses a trivial training problem : classifying images by color.
"""

import os
import glob
import numpy as np
import skimage.io as skio
import torch
import random
import tensorflow as tf
from tensorflow import keras
import json
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.applications import VGG16

os.system('pip install instaloader')

"""The following dictionaries, COLOR_DICT and COLOR_NAMES, are meant to store the colors recognized by the classifier (neural network) as it wil be trained. Each color is assigned an int, starting with 0 for red. The keys of both COLOR_DICT and COLOR_NAMES are those ints. COLOR_DICT has its values as lists of RBG values (floats ranging from 0.0 to 1.0), representing the RBG values of pure tones. COLOR_NAMES has its values as strings for the English names of the colors contained in COLOR_DICT"""

COLOR_DICT={ 0 : [1.0,0.2,0.1],
            1 : [0.9,0.7,0.1],
            2 : [1.0,1.0,0.1],
            3 : [0.1,1.0,0.2],
            4 : [0.1,1.0,1.0],
            5 : [0.1,0.2,1.0],
            6 : [0.8,0.1,1.0],
            7 : [1.0,1.0,1.0],
            8 : [0.6,0.6,0.6],
            9 : [0.5,0.3,0.2],
            10 : [0.01,0.01,0.01]
}

COLOR_NAMES={0 : 'red',
             1 : 'orange',
             2 : 'yellow',
             3 : 'green',
             4 : 'aqua',
             5 : 'blue',
             6 : 'violet',
             7 : 'white',
             8 : 'grey',
             9 : 'brown',
             10 : 'black'}

def randomly_filter(matrix, dxry=COLOR_DICT) -> np.ndarray:
  k=random.choice(list(dxry.keys()))
  f=np.asarray(dxry[k]).reshape(1,matrix.shape[2])
  matrix[:,:] *= f 
  v=np.zeros((len(dxry),1))
  v[k][0]+=1
  return v

def inequal_scalar(a,b):
  return int(a==b)

inequal = np.vectorize(inequal_scalar)

"""This program can automatically generate a testing set and a training set of color images (pure tones with random noise added). The training set should have dimensions (TRAIN_SIZE, HEIGHT, WIDTH, DEPTH) and the testing set should have dimensions (TEST_SIZE, HEIGHT, WIDTH, DEPTH)."""

TEST_SIZE = 2000 #number of images in automatically-generated testing set
TRAIN_SIZE=10000 #number of images 
HEIGHT, WIDTH, DEPTH = 100,100,3 #height, width, and depth of an input image

def generate_training_data(n_examples = TRAIN_SIZE,
                           h = HEIGHT,
                           w = WIDTH,
                           d = DEPTH,
                           dxry = COLOR_DICT,
                           factor = 0.2) -> tuple :
  x = np.random.randn(n_examples, h, w, d)
  y = np.zeros((n_examples, len(dxry), 1))
  x *= factor
  x += 1 - factor
  for i in range(n_examples):
    y[i] += randomly_filter(x[i], dxry)
  return x, y

def generate_testing_data(n_examples = TEST_SIZE,
                          h = HEIGHT,
                          w = WIDTH,
                          d = DEPTH,
                          dxry = COLOR_DICT,
                          ) -> tuple :
  g = generate_training_data(n_examples,h,w,d,dxry)
  return g

def train_model(model,
                eps = 20,
                bs = 50,
                n_examples = TEST_SIZE,
                h = HEIGHT,
                w = WIDTH,
                d = DEPTH,
                dxry = COLOR_DICT):
  x_train, y_train = generate_training_data(n_examples, h, w, d, dxry)
  model.fit(x_train, y_train,epochs=eps, batch_size=bs)

def test_model(model,
               n_examples = TEST_SIZE,
               h = HEIGHT,
               w = WIDTH,
               d = DEPTH,
               dxry = COLOR_DICT,
               verbose = 1) -> float :
  x_test,y_test = generate_testing_data(n_examples,h,w,d,dxry)
  y_pred = model.predict(x_test)
  a_test = np.argmax(y_test, axis=0)
  a_pred = np.argmax(y_pred, axis=0)
  inacc = inequal(a_test, a_pred)
  err = 1.0*np.sum(inacc)
  err /= n_examples
  acc = 1.0-err
  if verbose:
    s=f'Predicted with {100*acc} percent accuracy.\n'
    print(s)
  return acc

def show_color_mat(dxry=COLOR_DICT,
                h = HEIGHT,
                w = WIDTH,
                d = DEPTH) -> np.ndarray:
  x=np.zeros((h, w*len(dxry), d))
  for i in range(len(dxry)):
    start,stop=w*(i), w*(i+1)
    x[:,start:stop]=dxry[i]
  #skio.imshow(x)
  return x

def show_colors(dxry = COLOR_DICT,
                h = HEIGHT, 
                w = WIDTH,
                d = DEPTH) -> None:
  skio.imshow(show_color_mat(dxry, h,w, d))

def tile_matrix(img,
                h = HEIGHT,
                w = WIDTH,
                d = DEPTH) -> np.ndarray :
  vert_steps=int(img.shape[0] / h)
  horiz_steps=int(img.shape[1] / w )
  length = vert_steps * horiz_steps
  ret = []
  for i in range(length):
    horiz_corn=w*(i%horiz_steps)
    vert_corn=h*(i//horiz_steps)
    tile=img[vert_corn:vert_corn+h , horiz_corn:horiz_corn+w]
    ret.append(tile)
  ret = np.asarray(ret)
  return ret

def build_model(base_model, layer_list, n_freeze = 3, upstream_trainable = False):
  for layer in base_model.layers[:-1*n_freeze]:
    layer.trainable = upstream_trainable
  new_model = base_model.output
  for layer in layer_list:
    new_model = layer(new_model)
  ret = tf.keras.models.Model(inputs = base_model.input, 
                              outputs = new_model)
  return ret

model = VGG16(include_top=0, input_shape=(HEIGHT, WIDTH, DEPTH))
lay0 = Flatten()
lay1 = Dense(11, activation = 'softmax')
layer_list = [lay0,lay1]
model = build_model(model, layer_list)
#model.compile(optimizer = 'adam', loss = 'categorical_crossentropy')

"""Put model into JSON format for use in other models"""

with open('tbc_mod.json', 'w') as f:
  f.write(json.loads(json.dumps(model.to_json())))