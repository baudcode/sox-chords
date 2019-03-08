from math import log, pow

from sox_chords.music.base import Note, CoreNote
from sox_chords.music.mapping import SemiCoreToneMapping
from sox_chords.values import Values


def get_key(f=440.0, pitch=440.0):
    """
    Get piano key number from frequency
    :param f: frequency of the tone
    :param pitch: convert pitch of the orchestra 
    :return: key number
    """
    return int(log(f / pitch, 2) * 12 + 49)


def get_frequency(key=88, pitch=440.0):
    """
    Get frequency from piano key number
    :param key: key number of the piano
    :param pitch: convert pitch of the A4 note in Hz
    :return: frequency in hz
    """
    return pow(2, float(key - 49) / 12.0) * pitch


def note_to_freq(note=None):
    """
    Transforms a Note into a float frequency

    :param note: core.Note 
    :return: frequency in hz 
    """
    assert (isinstance(note, Note)), "note is not of instance Note"
    return get_frequency(key=(get_semi_tone(note)))


def get_notes_from_pattern(root=None, notation=None, core_pattern=None):

    print(root, notation, core_pattern)
    """
    Returns notes f.e. for a chord, with a given notation and core pattern

    :param root: root note
    :param notation: step size notation, e.g. [0,4,7] for a major triad or [0,3,7] for a minor triad
    :param core_pattern: core note differences of each step, e.g. a triad is [0,2,2] 
    :return: notes computed with the given parameters
    """
    assert(isinstance(root, Note)), "root is not of instance note"
    assert(notation is not None and core_pattern is not None), "notation or core pattern is null"
    assert(len(notation) == len(core_pattern)), "Notation and core pattern must have same size"

    notes = [root]
    for i in range(1, len(notation)):
        semi_tone = get_semi_tone(root, notation[i])
        core = get_core_from_diff(root, core_pattern[i])
        if Values.DEBUG:
            print("core: " + str(core), "Step:" + str(semi_tone), "Root core:" + str(root.get_core()), "Root step: "
                  + str(root.get_semi_tone()), SemiCoreToneMapping.semi_tones[semi_tone])
        assert (core in SemiCoreToneMapping.semi_tones[semi_tone]), \
            "No Note found for root " + str(root) + " and relative half step " +\
            str(notation[i]) + " with core note " + CoreNote.to_string(core)
        notes.append(
            SemiCoreToneMapping.semi_tones[semi_tone][core]
        )

    return notes


def get_note(name="", octave=4):
    """ 
        Get note from name
        :param name: C, C#, Cb, C##, Cbb, Bbb, B## ...
        :param octave: 1 to 8
    """
    assert(0 < octave < 9), str(octave) + " it not in 0 < octave < 9"
    note_name = name + str(octave)
    assert(note_name in SemiCoreToneMapping.notes), name + " is not a valid note"
    return SemiCoreToneMapping.notes[note_name]


def get_core_notes(octave=4):
    return list(map(lambda x: get_note(x, octave), Values.CORE_NOTES))


def get_semi_tone(root=None, step=2):
    assert (isinstance(root, Note)), "Root is not instance of note"
    return (root.get_semi_tone() + step) % Values.MAX_NUM_KEYS


def get_core_from_diff(root=None, diff=0):
    assert (isinstance(root, Note)), "Root is not instance of note"
    return (root.get_core() + diff) % Values.MAX_CORE_NOTES


def get_next_core(root=None, semi_tone_diff=0):

    semi_tone = root.get_semi_tone() % Values.MAX_SEMI_TONES
    core = root.get_core()
    while semi_tone_diff is not 0:
        if semi_tone in Values.IS_NEXT_CORE_SEMI_TONE:
            core = (core + 1) % Values.MAX_CORE_NOTES
        semi_tone = (semi_tone + 1) % Values.MAX_SEMI_TONES
        semi_tone_diff -= 1
    return core


def get_note_by_semi_tone_diff(root=None, semi_tone_diff=0):
    if Values.DEBUG:
        print("Root: " + str(root), "Semi Tone Diff: " + str(semi_tone_diff))
    semi_tone = get_semi_tone(root, semi_tone_diff)
    next_core = get_next_core(root, semi_tone_diff)
    if Values.DEBUG:
        print("Actual semi tone: " + str(semi_tone), "Next core: " + str(next_core))
    return SemiCoreToneMapping.semi_tones[semi_tone][next_core]
