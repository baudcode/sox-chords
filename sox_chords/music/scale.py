from abc import abstractproperty
from functools import reduce
import os

from sox_chords.music.base import Note
from sox_chords.music.base import NoteCollection
from sox_chords.util.sox import Sox
from sox_chords.music.utils import get_note_by_semi_tone_diff
from sox_chords.values import Values


class Scale(NoteCollection):

    def __init__(self, root=None):
        assert(reduce(lambda x, y: x + y, self.pattern) == Values.MAX_SEMI_TONES), self.__class__.__name__ + \
            " is not a valid scale"
        super(Scale, self).__init__(root, Scale.get_notes(root, self.pattern))

    @staticmethod
    def get_notes(root=None, pattern=None):
        assert (isinstance(root, Note)), "Root is not of instance note"
        assert (isinstance(pattern, list)), "pattern is not a list"

        semi_tone_diff = 0
        notes = []
        for i in range(len(pattern)):
            semi_tone_diff += pattern[i]
            notes.append(
                get_note_by_semi_tone_diff(root, semi_tone_diff)
            )
        return notes

    @abstractproperty
    def pattern(self):
        return []

    def get_name(self):
        return "%s_%s" % (self.root.get_name(), self.__class__.__name__)

    def generate(self, output_dir, extension='.wav', bits=16, sr=44100, dpn=1):
        output = os.path.join(output_dir, self.get_name() + extension)
        Sox.create_audio(notes=self.notes, output=output, dpn=dpn, bits=bits, sr=sr, duration=dpn * len(self.notes))
        return output


class MajorScale(Scale):

    pattern = [2, 2, 1, 2, 2, 2, 1]


class MinorScale(Scale):

    pattern = [2, 1, 2, 2, 1, 2, 2]


class HarmonicMinorScale(Scale):

    pattern = [2, 1, 2, 2, 1, 3, 1]


class MelodicMinorScale(Scale):

    pattern = [2, 1, 2, 2, 2, 2, 1]


scales = [MajorScale, MinorScale, HarmonicMinorScale, MelodicMinorScale]
