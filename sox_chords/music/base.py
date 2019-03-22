from abc import abstractmethod
from functools import reduce
from sox_chords.values import Values

class Interval(object):
    PERFECT_UNISON = 0
    MINOR_SECOND = 1
    MAJOR_SECOND = 2
    MINOR_THIRD = 3
    MAJOR_THIRD = 4
    PERFECT_FOURTH = 5
    TRITONE = 6
    PERFECT_FIFTH = 7
    MINOR_SIXTH = 8
    MAJOR_SIXTH = 9
    MINOR_SEVENTH = 10
    MAJOR_SEVENTH = 11
    PERFECT_OCTAVE = 12

    DIMINISHED_SECOND = 0
    AUGMENTED_UNISON = 1
    DIMINISHED_THIRD = 2
    AUGMENTED_SECOND = 3
    DIMINISHED_FOURTH = 4
    AUGMENTED_THIRD = 5
    DIMINISHED_FIFTH = 6
    AUGMENTED_FOURTH = 6
    DIMINISHED_SIXTH = 7
    AUGMENTED_FIFTH = 8
    DIMINISHED_SEVENTH = 9
    AUGMENTED_SIXTH = 10
    DIMINISHED_OCTAVE = 11
    AUGMENTED_SEVENTH = 12


class CoreNote(object):
    C, D, E, F, G, A, B = range(7)

    @staticmethod
    def to_string(val):
        if val is 0:
            return "C"
        elif val is 1:
            return "D"
        elif val is 2:
            return "E"
        elif val is 3:
            return "F"
        elif val is 4:
            return "G"
        elif val is 5:
            return "A"
        elif val is 6:
            return "B"
        else:
            return "Undefined"


semi_tone_core_mapping = {
    0: CoreNote.C,
    1: CoreNote.C,
    2: CoreNote.D,
    3: CoreNote.D,
    4: CoreNote.E,
    5: CoreNote.F,
    6: CoreNote.F,
    7: CoreNote.G,
    8: CoreNote.G,
    9: CoreNote.A,
    10: CoreNote.A,
    11: CoreNote.B,
}


class Note(object):
    """
        Note: Note to be played

        :param octave: octave of the tone like C4
        :param semi_tone: range 0 to MAX_NUM_KEYS (semi tone number on piano)
        :param core: core tone (0 = C, 1=D, 2=E...), Ebb has core (2=E)
        :param name: name of the tone
    """

    def __init__(self, core=0, semi_tone=0, name="Bb"):
        self.core = core
        self.semi_tone = semi_tone
        self.name = name
        self.octave = (semi_tone // 12) + 1

    def set_octave(self, octave=4):
        self.octave = octave

    def get_core(self):
        return self.core

    def set_semi_tone(self, semi_tone=0):
        self.semi_tone = semi_tone

    def get_name(self):
        return self.name

    def get_semi_tone(self):
        return self.semi_tone

    def get_octave(self):
        return self.octave

    @staticmethod
    def from_semitone(semi_tone):
        root = semi_tone % 12
        core = semi_tone_core_mapping[root]
        name = CoreNote.to_string(core)

        if root == 1 or root == 3 or root == 6 or root == 8 or root == 10:
            name += "#"
        return Note(core=core, semi_tone=semi_tone, name=name)

    @staticmethod
    def from_core_and_semi_tone(core, semi_tone):
        rel_semi_tone = semi_tone % Values.MAX_SEMI_TONES
        core_diff = rel_semi_tone - sum(Values.SEMI_TONE_STEPS[:core])
        name = CoreNote.to_string(core)
        if core_diff < 0:
            name += "b" * abs(core_diff)
        elif core_diff > 0:
            name += "#" * core_diff
        
        return Note(core=core, semi_tone=semi_tone, name=name)
        

    def __str__(self):
        return self.name + str(self.octave)

    def __repr__(self):
        return self.name + str(self.octave)
    
    def __eq__(self, other):
        if isinstance(other, Note):
            return other.core == self.core and other.semi_tone == self.semi_tone
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, Note):
            return other.core != self.core or other.semi_tone != self.semi_tone
        else:
            return True


class NoteCollection(object):
    def __init__(self, root=None, notes=None):
        assert (isinstance(root, Note))
        assert (isinstance(notes, list))
        self.root = root
        self.notes = notes

    def __str__(self):
        return "[" + reduce(lambda x, y: str(x) + "," + str(y), self.notes) + "]"

    def get_notes(self):
        return self.notes

    def get_root(self):
        return self.root

    @abstractmethod
    def generate(self, output_dir=""):
        """
        Generate an audio file of the notes

        :param output_dir: output directory of generated audio
        :return: true, if its created, else false
        """
        pass
