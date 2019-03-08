from sox_chords.music.base import Interval
from sox_chords.music.chords.triad import Triad


class Sus4(Triad):

    core_pattern = [0, 3, 4]
    notation = [0, Interval.PERFECT_FOURTH, Interval.PERFECT_FIFTH]
    name = "sus4"


class Sus2(Triad):

    core_pattern = [0, 1, 4]
    notation = [0, Interval.MAJOR_SECOND, Interval.PERFECT_FIFTH]
    name = "sus2"


chords = [Sus4, Sus2]
