import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import numpy as np
import cv2
import os
import pandas as pd
import ik_solver
import ws_client

SEQUENCE_LENGTH = 1          # number of frames per sample (start with 1)
IMAGE_HEIGHT = 128
IMAGE_WIDTH = 128
NUM_CHANNELS = 3             # RGB
OUTPUT_VECTOR_DIM = 6

def build_video_vector_model(input_shape, output_dim):
    model = keras.Sequential([
        # Input: (sequence_length, H, W, C)
        layers.Input(shape=input_shape),

        # TimeDistributed CNN (frame-wise feature extraction)
        layers.TimeDistributed(layers.Conv2D(32, (3, 3), activation='relu')),
        layers.TimeDistributed(layers.MaxPooling2D((2, 2))),

        layers.TimeDistributed(layers.Conv2D(64, (3, 3), activation='relu')),
        layers.TimeDistributed(layers.MaxPooling2D((2, 2))),

        layers.TimeDistributed(layers.Conv2D(128, (3, 3), activation='relu')),
        layers.TimeDistributed(layers.MaxPooling2D((2, 2))),

        # Flatten CNN output for each frame
        layers.TimeDistributed(layers.Flatten()),

        # LSTM across time (sequence of frame features)
        layers.LSTM(128, activation='tanh'),

        # Output: 6 angles (regression)
        layers.Dense(output_dim, activation='linear')
    ])
    return model

# Input shape: (SEQUENCE_LENGTH, H, W, C)
input_shape = (SEQUENCE_LENGTH, IMAGE_HEIGHT, IMAGE_WIDTH, NUM_CHANNELS)

model = build_video_vector_model(input_shape, OUTPUT_VECTOR_DIM)
model.compile(optimizer='adam', loss='mse')
model.summary()

