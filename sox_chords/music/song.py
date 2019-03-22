from sox_chords.music.chords.triad import MajorTriad, MinorTriad, AugmentedTriad, DiminishedTriad
from sox_chords.music.base import Note, NoteCollection
from sox_chords.music.chord import Chord
from sox_chords.util.sox import Sox, SoxBuilder, SoxException
from sox_chords.music.utils import note_to_freq
from functools import reduce


class SoxChord(object):

    def __init__(self, notes, fade=.1, dpn=.05, duration=2, freq_shift=0):
        self.notes = notes
        self.fade = fade
        self.dpn = dpn
        self.duration = duration
        self.freq_shift = freq_shift


class SoxSong(object):

    def __init__(self, sox_chords):
        self.sox_chords = sox_chords

    @property
    def notes(self):
        return reduce(lambda x, y: x + y, map(lambda x: x.notes, self.sox_chords))
    
    @property
    def freq_shifts(self):
        freq_shifts = [[chord.freq_shift] * (len(chord.notes)) for chord in self.sox_chords]
        return reduce(lambda x, y: x + y, freq_shifts)

    def generate(self, output, sr=44100, channels=1, norm=-1, bits=8, fade=.1, noise=None):
        
        notes = list(map(lambda x: Sox.check_note(x), self.notes))
        notes = [note_to_freq(note) + self.freq_shifts[k] for k, note in enumerate(notes)]

        fade = [0, sum(map(lambda x: x.duration, self.sox_chords)), fade]
        curdelay = 0
        delays = []

        for k, chord in enumerate(self.sox_chords):
            
            for delay in range(len(chord.notes)):
                delays.append(curdelay)
                curdelay += chord.dpn
            
            # add missing delay for next note
            curdelay += chord.duration - (chord.dpn * len(chord.notes))
        print(len(notes), len(delays))
        norm = [norm]
        return Sox.call(SoxBuilder(notes, delays).set_sampling_rate(sr).set_channels(channels).set_output(output).
                        set_bits(bits).set_noise(noise).add_effect("fade", fade).add_effect("norm", norm).build())