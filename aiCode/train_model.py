import os
import cv2
import numpy as np
import pandas as pd

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


# ========================
# PARAMETERS
# ========================

SEQUENCE_LENGTH = 1          # start with 1 frame per sample
IMAGE_HEIGHT = 128
IMAGE_WIDTH = 128
NUM_CHANNELS = 3             # RGB
OUTPUT_VECTOR_DIM = 6        # 6 servo angles

IMAGES_DIR = os.path.join('data', 'images')
LABELS_PATH = os.path.join('data', 'labels.csv')
MODEL_PATH = 'servo_angle_model.h5'


# ========================
# MODEL DEFINITION
# ========================

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


# ========================
# LOAD DATA
# ========================

def load_dataset(images_dir, labels_path):
    if not os.path.exists(labels_path):
        raise FileNotFoundError(f"labels.csv not found at {labels_path}")

    labels_df = pd.read_csv(labels_path)
    print("Loaded labels (first 5 rows):")
    print(labels_df.head())

    X = []  # sequences of frames
    Y = []  # 6-angle vectors

    for idx, row in labels_df.iterrows():
        filename = row['filename']
        img_path = os.path.join(images_dir, filename)

        img = cv2.imread(img_path)
        if img is None:
            print(f'Warning: could not open {img_path}, skipping.')
            continue

        # BGR -> RGB, resize, normalize
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (IMAGE_WIDTH, IMAGE_HEIGHT))
        img = img.astype(np.float32) / 255.0

        # Wrap into a sequence of length 1: shape (1, H, W, C)
        img_seq = np.expand_dims(img, axis=0)

        # Read angles
        angles = np.array([
            row['a1'], row['a2'], row['a3'],
            row['a4'], row['a5'], row['a6']
        ], dtype=np.float32)

        # Optional: normalize angles to roughly [-1, 1]
        # Adjust this if your angles are not in [-180, 180]
        angles = angles / 180.0

        X.append(img_seq)
        Y.append(angles)

    X = np.array(X, dtype=np.float32)
    Y = np.array(Y, dtype=np.float32)

    print('\nFinal dataset shapes:')
    print('X shape:', X.shape)  # (num_samples, 1, H, W, 3)
    print('Y shape:', Y.shape)  # (num_samples, 6)

    if X.shape[0] == 0:
        raise RuntimeError("No images loaded. Check your data/images folder and labels.csv filenames.")

    return X, Y


# ========================
# MAIN TRAIN FUNCTION
# ========================

def main():
    print("TensorFlow version:", tf.__version__)

    # Build model
    input_shape = (SEQUENCE_LENGTH, IMAGE_HEIGHT, IMAGE_WIDTH, NUM_CHANNELS)
    model = build_video_vector_model(input_shape, OUTPUT_VECTOR_DIM)
    model.compile(optimizer='adam', loss='mse')
    model.summary()

    # Load data
    X, Y = load_dataset(IMAGES_DIR, LABELS_PATH)

    # Train/val split
    X_train, X_val, Y_train, Y_val = train_test_split(
        X, Y, test_size=0.2, random_state=42
    )

    print('Train size:', X_train.shape[0])
    print('Val size:', X_val.shape[0])

    # Train
    EPOCHS = 20
    BATCH_SIZE = 8

    history = model.fit(
        X_train,
        Y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_val, Y_val)
    )

    # Optional: show basic loss values
    print('Final training loss:', history.history['loss'][-1])
    print('Final validation loss:', history.history['val_loss'][-1])

    # Save model
    model.save(MODEL_PATH)
    print(f'Model saved to {MODEL_PATH}')

    # Quick prediction check on one validation sample
    sample_seq = X_val[0:1]  # shape (1, 1, H, W, 3)
    true_angles_norm = Y_val[0]

    pred_norm = model.predict(sample_seq)[0]

    true_angles_deg = true_angles_norm * 180.0
    pred_angles_deg = pred_norm * 180.0

    print('True angles (deg):', true_angles_deg)
    print('Predicted angles (deg):', pred_angles_deg)


if __name__ == '__main__':
    main()