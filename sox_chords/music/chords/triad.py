# -*- coding: utf-8 -*-

from sox_chords.music.base import Interval

from sox_chords.music.chord import Chord
from sox_chords.music.utils import get_notes_from_pattern


class Triad(Chord):

    core_pattern = [0, 2, 4]
    notation = []
    name = "Triad"

    def __init__(self, root=None):
        super(Triad, self).__init__(root=root, notes=get_notes_from_pattern(root, self.notation, self.core_pattern))


class MajorTriad(Triad):

    notation = [0, Interval.MAJOR_THIRD, Interval.PERFECT_FIFTH]
    name = ""


class MinorTriad(Triad):

    notation = [0, Interval.MINOR_THIRD, Interval.PERFECT_FIFTH]
    name = "m"


class AugmentedTriad(Triad):

    notation = [0, Interval.MAJOR_THIRD, Interval.AUGMENTED_FIFTH]
    name = "+"


class DiminishedTriad(Triad):

    notation = [0, Interval.MINOR_THIRD, Interval.DIMINISHED_FIFTH]
    name = "°"


chords = [MajorTriad, MinorTriad, AugmentedTriad, DiminishedTriad]
