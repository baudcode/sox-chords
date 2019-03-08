from subprocess import check_output
from functools import reduce
from abc import abstractmethod

from sox_chords.music.base import Note
from sox_chords.music.mapping import SemiCoreToneMapping
from sox_chords.music.utils import get_core_from_diff, note_to_freq
from sox_chords.util.logger import logger


class SoxBuilder(object):

    # supported_effects = {name : num_of_args}
    supported_effects = {"fade": 3, "norm": 1}  # -1 = len of notes

    def __init__(self, notes=None, delays=None):
        assert(isinstance(notes, list) and isinstance(
            delays, list)), "Notes or delays not a list"
        assert (len(notes) != 0), "You must set some notes"
        assert(len(notes) == len(delays)
               ), "size of delays and notes list must be equal"
        self.notes = notes
        self.delays = delays
        self.effects = []
        self.bits = 24
        self.channels = 1
        self.noise = None
        self.sampling_rate = 44100
        self.output = "out.wav"

    def set_noise(self, noise):
        if noise is not None:
            assert isinstance(noise, Noise), "noise is not of instance Noise"
            self.noise = noise.__class__.__name__.lower()
        return self

    def set_bits(self, bits):
        """
        Set the number of bits for the encoding

        :param bits: bit size of output quality (8,16,24,32)
        :return: self
        """
        assert (0 < bits < 33), "Bits not between 1 and 32"
        self.bits = bits
        return self

    def add_effect(self, name="", params=None):
        """
        Adds an effect to the created audio

        :param name: effect name e.g. norm or fade
        :param params: list, parameters for this effect
        :return: self
        """
        assert(name in self.supported_effects), "Effect " + \
            name + " is not supported"
        assert ((len(params) == len(self.notes) and self.supported_effects[name] == -1) or len(params) == self.supported_effects[name]), "Insufficient arguments for effect %s" % name

        self.effects.append([name, params])
        return self

    def set_sampling_rate(self, sampling_rate=44100):
        """
        Sets the output sampling rate

        :param sampling_rate: sampling rate must be between 44100 and 48000 hz
        :return: self
        """
        assert(44100 <= sampling_rate <= 48000), "Sampling rate " + \
            str(sampling_rate) + " is an invalid sampling rate"
        self.sampling_rate = sampling_rate
        return self

    def set_channels(self, channels=1):
        """
        Set number of output channels

        :param channels: number of output channels
        :return: self
        """
        self.channels = channels
        return self

    def set_output(self, output=""):
        """
        Sets the output file name

        :param output: output file name
        :return: self
        """
        self.output = output
        return self

    def build(self):
        args = []
        args.append("sox")
        args.append("--multi-threaded")

        args.append("-n")
        args.append("-c")
        args.append(str(self.channels))
        args.append("-r")
        args.append(str(self.sampling_rate))
        args.append("-b")
        args.append(str(self.bits))
        args.append(self.output)
        args.append("synth")
        for note in self.notes:
            args.append("pl")
            args.append(str(note))
        if self.noise:
            args.append(self.noise)

        args.append("delay")
        args += list(map(lambda x: str(x), self.delays))

        if len(self.effects) > 0:
            args.append("remix")
            args.append("-")

        for effect in self.effects:
            args.append(effect[0])
            args += list(map(lambda x: str(x), effect[1]))

        return args


class Noise:
    pass


class WhiteNoise(Noise):
    pass


class BrownNoise(Noise):
    pass


class TpdfNoise(Noise):
    pass


class Sox(object):

    @staticmethod
    def create_audio(output="", notes=None, sr=44100, fade=.1, dpn=.05, duration=2, channels=1, norm=-1, bits=8,
                     freq_shift=0, noise=None):
        """
        :param output: if output is not empty, file will be recorded to disk, else will be played
        :param notes: list of notes
        :param channels: number of audio channels
        :param sr: sampling_rate must be for pluck instruments between 44100 and 48000
        :param dpn: delay per note
        :param duration: duration of the audio in seconds
        :param fade: delay of the fade 1 = no delay
        :param norm: normalization
        :param bits: bits per sample value
        :param freq_shift: frequency shift by Hz
        :param noise: instance of class noise
        :return: true or false whether executed correctly
        """
        notes = list(map(lambda x: Sox.check_note(x), notes))
        if freq_shift != 0:
            notes = list(
                map(lambda note: note_to_freq(note) + freq_shift, notes))
        fade = [0, duration, fade]
        delays = []
        for delay in range(len(notes)):
            delays.append(dpn * delay)

        norm = [norm]
        return Sox.call(SoxBuilder(notes, delays).set_sampling_rate(sr).set_channels(channels).set_output(output).
                        set_bits(bits).set_noise(noise).add_effect("fade", fade).add_effect("norm", norm).build())

    @staticmethod
    def check_note(note=None):
        """
        Checks the note and returns a valid note
        Notes with double b and double # are not supported in sox

        :param note: a Note
        :return: valid Note
        """
        assert (isinstance(note, Note)), "Notes are not a list"

        """
        if "##" in note.get_name():
            return SemiCoreToneMapping.semi_tones[note.get_semi_tone()][get_core_from_diff(note, 1)]
        elif "bb" in note.get_name():
            return SemiCoreToneMapping.semi_tones[note.get_semi_tone()][get_core_from_diff(note, -1)]
        else:
            return note
        """
        return Note.from_semitone(note.get_semi_tone())

    @staticmethod
    def reduce_sampling_rate(in_file="", out_file="", rate=44100):
        Sox.call(["sox", in_file, "-r", str(rate), " ", out_file])

    @staticmethod
    def reduce_bits(in_file="", out_file="", bits=8):
        Sox.call(["sox", in_file, "-b", str(bits), " ", out_file])

    @staticmethod
    def call(args):
        try:
            logger.debug("[*] calling sox with: %s" %
                         reduce(lambda x, y: str(x) + " " + str(y), args))
            output = check_output(args)
            if output != b'':
                raise SoxException("Sox command " + reduce(lambda x, y: x + " " + y, args) + " failed with error: " + str(output))
        except OSError as e:
            raise SoxException(
                "Could not find sox, please install sox. sudo apt-get install sox")


class SoxException(Exception):
    pass


if __name__ == "__main__":
    from sox_chords.music.chords.triad import MajorTriad
    from sox_chords.music.utils import get_note
    import os
    print(os.path.dirname(os.path.realpath(__file__)))

    root = get_note("C", 4)
    m = MajorTriad(root)
    Sox.create_audio(notes=m.get_notes(), output=str(root) + ".wav", freq_shift=0, noise=TpdfNoise())
