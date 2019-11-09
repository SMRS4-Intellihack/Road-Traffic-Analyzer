# -*- coding: utf-8 -*-
"""e2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1z493eMYMsZ8EcmiDd4NEDlRdE65lPlO8
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

!pip install pydub
!apt install -y ffmpeg

from pydub import AudioSegment

import keras
from keras.layers import Activation, Dense, Dropout, Conv2D, \
                         Flatten, MaxPooling2D
from keras.models import Sequential
import librosa
import librosa.display
import numpy as np

from sklearn.model_selection import train_test_split

import warnings
warnings.filterwarnings('ignore')

data = pd.read_csv("metadata.csv")
evaluate_count = 6

dataset_X = []
dataset_y = []

for row in data.itertuples():
    y, sr = librosa.load('./audio/' + row.audio_class + '.wav', duration=18)  
    ps = librosa.feature.melspectrogram(y=y, sr=sr)
    if ps.shape == (128, 776):
      dataset_X.append(ps)
      dataset_y.append(row.native_lang_id)

classes = ['ambulance_siren','police_siren','fire_truck_siren','vehicle_skidding','car_crash','tire_squeal']
X = dataset_X
y = dataset_y

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.4)

# Reshape for CNN input
X_train = np.array([x.reshape( (128, 776, 1) ) for x in X_train])
X_test = np.array([x.reshape( (128, 776, 1) ) for x in X_test])

y_train = np.array(keras.utils.to_categorical(y_train, len(languages)))
y_test = np.array(keras.utils.to_categorical(y_test, len(languages)))

print(X_train.shape[0], 'training samples')
print(X_test.shape[0], 'testing samples')

model = Sequential()
input_shape=(128, 776, 1)

model.add(Conv2D(24, (5, 5), strides=(1, 1), input_shape=input_shape))
model.add(MaxPooling2D((4, 2), strides=(4, 2)))
model.add(Activation('relu'))

model.add(Conv2D(48, (5, 5), padding="valid"))
model.add(MaxPooling2D((4, 2), strides=(4, 2)))
model.add(Activation('relu'))

model.add(Conv2D(48, (5, 5), padding="valid"))
model.add(Activation('relu'))

model.add(Flatten())
model.add(Dropout(rate=0.5))

model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(rate=0.5))

model.add(Dense(len(languages)))
model.add(Activation('softmax'))

model.compile(
	optimizer="Adam",
	loss="categorical_crossentropy",
	metrics=['accuracy'])

model.fit(
	x=X_train, 
	y=y_train,
    epochs=35,
    batch_size=128,
    validation_data= (X_test, y_test))

score = model.evaluate(
	x=X_test,
	y=y_test)

print('Test loss:', score[0])
print('Test accuracy:', score[1])

model.save('./traffic.h5')

for i in range(evaluate_count):
  if os.path.exists('./evaluate/audio'+i+'.wav'):
    for j in range(60):
        y, sr = librosa.load('./evaluate/audio'+i+'.wav', offset=(10*j) duration=10)
        X_to_predict = librosa.feature.melspectrogram(y=y, sr=sr)
        X_to_predict = [X_to_predict.reshape( (1, 128, 776, 1) )]
        class_id = model.predict_classes(X_to_predict, batch_size=128, verbose=0)
        languages[class_id[0]]