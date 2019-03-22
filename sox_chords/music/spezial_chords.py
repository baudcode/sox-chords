
import itertools
import numpy as np
from sox_chords.music.utils import get_note, get_semi_tone, get_core_from_diff
from sox_chords.music.chord import Chord
from sox_chords.music.chords import triad
from sox_chords.music.base import CoreNote, Note
from sox_chords.values import Values

def _get_chord_progression(root_note, chord_classes, steps=Values.SEMI_TONE_STEPS):
    progression = [chord_classes[0](root_note)]

    note = root_note
    for k, chord in enumerate(chord_classes[1:]):
        next_core = get_core_from_diff(note, 1)
        next_semi_tone = get_semi_tone(note, steps[k])
        note = Note.from_core_and_semi_tone(core=next_core, semi_tone=next_semi_tone)
        progression.append(chord(note))
    
    return progression
    
def major_chord_progression(root_note):
    # C = I ii iii IV V vi vii0 viii
    # Major, Minor, Minor, Major, Major, Minor, Diminished
    chords = [triad.MajorTriad, triad.MinorTriad, triad.MinorTriad, triad.MajorTriad, triad.MajorTriad, triad.MinorTriad, triad.DiminishedTriad]
    return _get_chord_progression(root_note, chords, steps=Values.MAJOR_SEMI_TONE_STEPS)


def minor_chord_progression(root_note):
    # i ii0 III iv v VI VII
    chords = [triad.MinorTriad, triad.DiminishedTriad, triad.MajorTriad, triad.MinorTriad, triad.MinorTriad, triad.MajorTriad, triad.MajorTriad]
    return _get_chord_progression(root_note, chords, steps=Values.MINOR_SEMI_TONE_STEPS)


def guitar_coords(chords):
    guitar_coords = []
    # mash up chords so that all combinations from E2 to E5 are in there
    for chord in chords:
        note_names = [c.name for c in chord.notes]

        # generate all inversions available on guitar
        notes = [[get_note(name=name, octave=i) for i in range(2, 6)]
                 for name in note_names]
        comninations = list(itertools.product(*notes))

        # add 3 random notes from notes list and octave range
        for k in range(len(comninations)):
            comninations[k] = list(comninations[k])
            for i in range(3):
                rand_name = note_names[np.random.randint(0, len(note_names))]
                rand_octave = np.random.randint(2, 6)
                comninations[k].append(get_note(rand_name, rand_octave))

            # create a new chord from this combination
            root = list(filter(lambda x: x.name == chord.root.name, comninations[k]))[0]
            c = Chord(root=root, notes=comninations[k])
            c.name = chord.name
            guitar_coords.append(c)
    return guitar_coords
