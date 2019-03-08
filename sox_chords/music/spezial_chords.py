
import itertools
import numpy as np
from sox_chords.music.utils import get_core_notes, get_note
from sox_chords.music.chord import Chord


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
