from sox_chords.music.spezial_chords import major_chord_progression, minor_chord_progression
from sox_chords.music.utils import get_note
from sox_chords.music.chords.triad import MajorTriad, MinorTriad, DiminishedTriad

def test_major_chord_progression():
    root = get_note("C")
    progression = major_chord_progression(root)
    fixed_c_major_progression = [
        MajorTriad(get_note("C")),
        MinorTriad(get_note("D")),
        MinorTriad(get_note("E")),
        MajorTriad(get_note("F")),
        MajorTriad(get_note("G")),
        MinorTriad(get_note("A")),
        DiminishedTriad(get_note("B")),
    ]
    print(progression)
    assert (progression == fixed_c_major_progression)
    
def test_minor_chord_progression():
    root = get_note("C")
    progression = minor_chord_progression(root)
    fixed_c_major_progression = [
        MinorTriad(get_note("C")),
        DiminishedTriad(get_note("D")),
        MajorTriad(get_note("Eb")),
        MinorTriad(get_note("F")),
        MinorTriad(get_note("G")),
        MajorTriad(get_note("Ab")),
        MajorTriad(get_note("Bb")),
    ]
    print (progression)
    print([p.get_name() for p in progression])
    print([p.get_name() for p in fixed_c_major_progression])
    assert(progression == fixed_c_major_progression)