import music21 as music
import math

SAMPLES_PER_BEAT = 4

def read_midi(filename):
    score = music.converter.parse(filename)
    all_notes = []
    for i in range(math.ceil(score.duration.quarterLength * SAMPLES_PER_BEAT)):
        all_notes.append([0] * 48)

    for note in score.flat.notes:
        for pitch in note.pitches:
            while pitch.octave < 1:
                pitch.octave += 1
            while pitch.octave > 4:
                pitch.octave -= 1

            start_beat = math.floor(note.offset * SAMPLES_PER_BEAT)
            end_beat = math.ceil((note.offset + note.duration.quarterLength) * SAMPLES_PER_BEAT)
            simple_pitch = pitch.midi - 24

            for i in range(start_beat, end_beat + 1):
                if i > 0 and i < len(all_notes):
                    all_notes[i][simple_pitch] = 1

    return all_notes

def write_midi(filename, notes_vectors):
    stream = music.stream.Stream()
    for i in range(len(notes_vectors[0])):
        last_active = False
        note = None
        offset = None
        for x in range(len(notes_vectors) + 1):
            active = x < len(notes_vectors) and notes_vectors[x][i] == 1

            if active and not last_active:
                note = music.note.Note(24 + i)
                note.duration.quarterLength = 1 / SAMPLES_PER_BEAT
                offset = x / SAMPLES_PER_BEAT

            elif active and last_active:
                note.duration.quarterLength += 1 / SAMPLES_PER_BEAT

            elif not active and last_active:
                stream.insert(offset, note)

            last_active = active

    stream.write("midi", fp=filename)
