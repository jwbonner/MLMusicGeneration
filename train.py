import midi_interface
import os
import numpy as np
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.initializers import RandomNormal
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
import multiprocessing
import random

FOLDER = "datasets/maestro-v3.0.0/2018"
PREDICTOR_LENGTH = 80
SEQUENCE_LENGTH = PREDICTOR_LENGTH + 1
NOTE_COUNT = 48
VALIDATION_PERCENT = 0.1

def decode_midi(filename):
    print(filename)
    input_sequences = []
    partial_sequences = []
    input_sequence = midi_interface.read_midi(FOLDER + "/" + filename)
    input_sequences.append(input_sequence)
    for start in range(0, len(input_sequence) - SEQUENCE_LENGTH + 1):
        partial_sequence = input_sequence[start:start + SEQUENCE_LENGTH]
        if (partial_sequence[-1]) != [0] * NOTE_COUNT:
            partial_sequences.append(partial_sequence)
    return partial_sequences

if __name__ == "__main__":
    print("\nReading MIDI files")
    filenames = os.listdir(FOLDER)[:40]
    print(len(filenames), "files")
    pool = multiprocessing.Pool()
    partial_sequence_results = pool.map(decode_midi, filenames)
    partial_sequences_train = []
    partial_sequences_valid = []
    for result in partial_sequence_results:
        for sequence in result:
            if random.random() > VALIDATION_PERCENT:
                partial_sequences_train.append(sequence)
            else:
                partial_sequences_valid.append(sequence)
    partial_sequences_train = np.array(partial_sequences_train)
    partial_sequences_valid = np.array(partial_sequences_valid)
    print(len(partial_sequences_train), "training sequences,", len(partial_sequences_valid), "validation sequences")

    # Create model
    initializer = RandomNormal(mean=0.0, stddev=1.0)
    model = Sequential()
    model.add(LSTM(128, kernel_initializer=initializer, return_sequences=True, input_shape=(PREDICTOR_LENGTH, NOTE_COUNT)))
    model.add(Dropout(0.5))
    model.add(LSTM(64, kernel_initializer=initializer, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(32, kernel_initializer=initializer, return_sequences=False))
    model.add(Dropout(0.1))
    model.add(Dense(NOTE_COUNT, activation="sigmoid", kernel_initializer=initializer))
    model.summary()
    model.compile(loss=BinaryCrossentropy(from_logits=True), optimizer=Adam(learning_rate=0.0001), metrics=["binary_accuracy"])

    # Train model
    predictors_train = partial_sequences_train[:,:-1]
    predictors_valid = partial_sequences_valid[:,:-1]
    labels_train = partial_sequences_train[:,-1]
    labels_valid = partial_sequences_valid[:,-1]
    model.fit(predictors_train, labels_train, epochs=25, verbose=1, validation_data=(predictors_valid, labels_valid))
    model.save("music_model")