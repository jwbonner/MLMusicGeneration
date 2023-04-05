import os
import midi_interface
import tensorflow.keras as keras
import numpy as np
import train
import random

OUTPUT_LENGTH = 500
PLAY_SENSITIVITY = 0.95
PREDICTOR_LENGTH = train.PREDICTOR_LENGTH
NOTE_COUNT = train.NOTE_COUNT
FOLDER = train.FOLDER

if __name__ == "__main__":
    model = keras.models.load_model("music_model")
    output_sequence = []
    input_sequence = []

    # Read input sequence from file
    filename = os.listdir(FOLDER)[0]
    print("Seed file =", filename)
    input_sequence = midi_interface.read_midi(FOLDER + "/" + filename)[:PREDICTOR_LENGTH]

    # Generate outputs
    while len(output_sequence) < OUTPUT_LENGTH:
        next_note = model.predict(np.array([input_sequence]), verbose=0)[0] 
        next_note_output = [1 if x > PLAY_SENSITIVITY else 0 for x in next_note]
        print(len(output_sequence), next_note_output)
        output_sequence.append(next_note_output)
        input_sequence.append(next_note)
        input_sequence.pop(0)

    # Save result
    midi_interface.write_midi("test_music.midi", output_sequence)