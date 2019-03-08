from sox_chords.music.utils import get_core_notes, get_note
import sox_chords.music.chords.seventh
import sox_chords.music.chords.sus
import sox_chords.music.chords.triad
from sox_chords.music.utils import get_note
from sox_chords.util.logger import logger
from sox_chords.values import Values

chord_classes = []
# chord_classes += seventh.chords
chord_classes += sus.chords
chord_classes += triad.chords
chord_classes += seventh.chords

__all__ = [chord.__name__ for chord in chord_classes]


def get_all_chords(octave=4, debug=False):
    root_notes = []
    for core_note in Values.CORE_NOTES:
        root_notes.append(get_note(core_note, octave=octave))
        root_notes.append(get_note(core_note + "b", octave=octave))

    # for debugging
    chords = []
    for chord in chord_classes:
        for note in root_notes:
            logger.debug("Chord ", chord.__name__, " for root note ", note.get_name())
            chords.append(chord(note))
    return chords
    # return [[chord(note) for note in root_notes] for chord in chord_classes]
