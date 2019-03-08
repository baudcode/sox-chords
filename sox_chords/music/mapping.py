from copy import copy

from sox_chords.music.base import Note, CoreNote
from sox_chords.values import Values


def create_note(root=None, semi_tone_diff=-1, append="b"):
    if (root.get_semi_tone() + semi_tone_diff) < 0:
        return None
    if (root.get_semi_tone() + semi_tone_diff) > (Values.MAX_NUM_KEYS - 1):
        return None
    note = Note(root.get_core(), (root.get_semi_tone() + semi_tone_diff) %
                Values.MAX_NUM_KEYS, root.get_name() + append)

    return note


def create_notes(octave_start=1, octave_end=8):
    core_notes = [
        Note(CoreNote.C, 0, "C"),
        Note(CoreNote.D, 2, "D"),
        Note(CoreNote.E, 4, "E"),
        Note(CoreNote.F, 5, "F"),
        Note(CoreNote.G, 7, "G"),
        Note(CoreNote.A, 9, "A"),
        Note(CoreNote.B, 11, "B"),
    ]
    _all_notes = {}
    semi_tones = {}
    for octave in range(octave_start, octave_end + 1):
        for core_note in core_notes:
            note = copy(core_note)
            note.set_octave(octave)
            note.set_semi_tone(note.get_semi_tone() + ((octave - 1) * Values.MAX_SEMI_TONES))

            note_b = create_note(root=note, semi_tone_diff=-1, append="b")
            note_bb = create_note(root=note, semi_tone_diff=-2, append="bb")
            note_bbb = create_note(root=note, semi_tone_diff=-3, append="bbb")
            note_sharp = create_note(root=note, semi_tone_diff=1, append="#")
            note_sharp_sharp = create_note(root=note, semi_tone_diff=2, append="##")
            note_sharp_sharp_sharp = create_note(root=note, semi_tone_diff=3, append="###")
            new_notes = [note, note_b, note_bb, note_bbb, note_sharp, note_sharp_sharp, note_sharp_sharp_sharp]

            for n in new_notes:
                if n is not None:
                    _all_notes[str(n)] = copy(n)
                    if n.get_semi_tone() not in semi_tones:
                        semi_tones[n.get_semi_tone()] = {}

                    semi_tones[n.get_semi_tone()][n.get_core()] = copy(n)
                    if Values.DEBUG:
                        print(n.get_semi_tone(), n.get_core(), n.get_name())
    if Values.DEBUG:
        for semi_tone in semi_tones:
            print(semi_tone, ":",
                  [str(semi_tones[semi_tone][core]) for core in [core for core in semi_tones[semi_tone]]])

    return _all_notes, semi_tones


class SemiCoreToneMapping(object):
    notes, semi_tones = create_notes()
