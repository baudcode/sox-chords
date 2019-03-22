from sox_chords.music.song import SoxChord, SoxSong
from sox_chords.music.chords import get_note
from sox_chords.music.chords import triad
import tempfile
from sox_chords.music.spezial_chords import major_chord_progression, minor_chord_progression

def test_create_sox_song():

    progression = [triad.MajorTriad(get_note("C")), \
        triad.MajorTriad(get_note("F")), \
        triad.MajorTriad(get_note("G"))]
    progression = map(lambda chord: SoxChord(chord.notes, duration=1), progression)
    song = SoxSong(progression)
    
    output = tempfile.mktemp(suffix='.wav')
    song.generate(output)
    print ("creating song %s" % output)

def test_create_song_from_chord_progression():

    root = get_note("C")
    progression = minor_chord_progression(root)

    progression = map(lambda chord: SoxChord(chord.notes, duration=1), progression)
    song = SoxSong(progression)
    
    output = tempfile.mktemp(suffix='.wav')
    song.generate(output)
    print ("creating song %s" % output)