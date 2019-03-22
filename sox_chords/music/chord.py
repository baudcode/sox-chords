from abc import abstractproperty
from os.path import join

from sox_chords.music.base import NoteCollection
from sox_chords.util.sox import Sox


class Chord(NoteCollection):
    """
        chords class to inherit from
    """
    name = ""

    def __init__(self, root=None, notes=None):
        super(Chord, self).__init__(root, notes)

    def __str__(self):
        return self.root.get_name() + self.name + ": " + super(Chord, self).__str__()

    def __repr__(self):
        return self.get_name()

    def get_name(self):
        return self.root.get_name() + self.name

    def generate(self, output_dir="", extension=".wav", duration=1.0, sr=44100, bits=16, noise=None, freq_shift=0):
        output = join(output_dir, self.get_name() + extension)
        Sox.create_audio(output=output, notes=self.notes, duration=duration, fade=0, dpn=0, bits=bits, sr=sr,
                         noise=noise, freq_shift=freq_shift)
        return output

    def __eq__(self, other):
        if isinstance(other, Chord):
            return self.notes == other.notes
        else:
            return False
            
    def __ne__(self, other):
        if isinstance(other, Chord):
            return self.notes != other.notes
        else:
            return True
