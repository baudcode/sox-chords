# -*- coding: utf-8 -*-

from sox_chords.music.base import Interval
from sox_chords.music.chords.triad import Triad


class Seventh(Triad):

    core_pattern = Triad.core_pattern + [6]
    name = "Seventh"


class DominantSeventh(Seventh):

    notation = [0, Interval.MAJOR_THIRD, Interval.PERFECT_FIFTH, Interval.MINOR_SEVENTH]
    name = "7"


class MajorSeventh(Seventh):

    notation = [0, Interval.MAJOR_THIRD, Interval.PERFECT_FIFTH, Interval.MAJOR_SEVENTH]
    name = "M7"


class MinorSeventh(Seventh):

    notation = [0, Interval.MINOR_THIRD, Interval.PERFECT_FIFTH, Interval.MINOR_SEVENTH]
    name = "m7"


class MinorMajorSeventh(Seventh):

    notation = [0, Interval.MINOR_THIRD, Interval.PERFECT_FIFTH, Interval.MAJOR_SEVENTH]
    name = "nM7"


class AugmentedMajorSeventh(Seventh):

    notation = [0, Interval.MAJOR_THIRD, Interval.AUGMENTED_FIFTH, Interval.MAJOR_SEVENTH]
    name = "+M7"


class AugmentedSeventh(Seventh):

    notation = [0, Interval.MAJOR_THIRD, Interval.AUGMENTED_FIFTH, Interval.MINOR_SEVENTH]
    name = "+7"


class DiminishedSeventh(Seventh):

    notation = [0, Interval.MINOR_THIRD, Interval.DIMINISHED_FIFTH, Interval.DIMINISHED_SEVENTH]
    name = "°7"


class HalfDiminishedSeventh(Seventh):

    notation = [0, Interval.MINOR_THIRD, Interval.DIMINISHED_FIFTH, Interval.MINOR_SEVENTH]
    name = "ø7"


chords = [MajorSeventh, MinorSeventh, DominantSeventh, MinorMajorSeventh, AugmentedSeventh, AugmentedMajorSeventh,
          DiminishedSeventh, HalfDiminishedSeventh]
