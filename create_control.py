import midi_interface
import os
import train

FOLDER = train.FOLDER

if __name__ == "__main__":
    filename = os.listdir(FOLDER)[0]
    notes = midi_interface.read_midi(FOLDER + "/" + filename)
    midi_interface.write_midi("converted_music.midi", notes)