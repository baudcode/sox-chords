from argparse import ArgumentParser
from abc import abstractmethod

""" Chord Processor imports"""
from random import randint
from numpy.random import permutation
from os.path import join, exists
from pickle import load as pickle_load
import pickle
import tqdm
import numpy as np

from sox_chords.exceptions import ReaderException
from sox_chords.music import utils
from sox_chords.util.generators import AudioFrameGenerator
from sox_chords.util.visualize import get_visual_data, power_spectrogram, dpi, show_images
from sox_chords.values import Values
from sox_chords.util.logger import pp
from sox_chords.util.logger import logger


class BatchProcessor:
    def __init__(self):
        self._input_data = None

    @abstractmethod
    def batch_iterator(self, batch_size=20):
        pass

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, x):
        self._input_data = x


class AudioProcessor(BatchProcessor):

    def __init__(self, audio_files, labels, sr=44100, frame_length=1.0, v_func=power_spectrogram, bw=False,
                 v_size=(96, 96)):
        super().__init__()
        assert(len(audio_files) == len(labels)
               ), "audio files size must be equal to labels size"
        self.labels = labels
        self.audio_files = audio_files
        self.sr = sr
        self.frame_length = frame_length
        self.bw = bw
        self.v_func = v_func
        self.v_size = v_size
        self.fg = self.fg = [(self.labels[i],
                              AudioFrameGenerator(self.audio_files[i], sr=self.sr, load_duration=self.frame_length))
                             for i in range(len(self.labels))]

    def batch_iterator(self, batch_size=100, test=False, one_hot=True, n_batches=5000, n_mixed_files=5,
                       rand_chord_sample=True, rand_mix_sample=True, rand_chord=True):
        """
        Returns the next batch needed for feeding into the network


        frame dimension: 1x22050 (for 1 second of audio)
        -> modify frame by overlaying samples
        -> generate visualization using v_func
        ->

        :param batch_size: int, number of batches
        :param test: bool, get test data
        :param one_hot: bool, make y one hot
        :param n_mixed_files: int, number of files mixed with input chord
        :param n_batches: int, number of batches in 1 epoch
        :param rand_chord_sample: bool, randomize chord input sample
        :param rand_mix_sample: bool, randomize mix file samples
        :param rand_chord: bool, randomize getting new chord or get them in order
        :param bw: bool, convert visualization to gray scale
        :return: x,y
        """
        classes = len(self.labels)
        idxs = len(self.fg)
        o_index = -1

        if Values.DEBUG:
            pp("Generating " + str(n_batches) + " batches")
        for batch_i in range(n_batches):
            x, y = [], []
            while len(x) < batch_size:
                if len(x) % 5 == 0 and Values.DEBUG:
                    pp(str(len(x)) + " of " + str(batch_size))

                # Get Random Input Chord or
                if rand_chord:
                    o_index = np.random.randint(idxs)
                else:
                    o_index = (o_index + 1) % idxs

                (key, orig_fg) = self.fg[o_index]
                if Values.DEBUG:
                    pp("Use chord: " + str(key))

                for frame in orig_fg.get_frames(frame_length=self.frame_length, num_frames=1,
                                                randomize=rand_chord_sample):

                    if one_hot:
                        y.append(
                            [1 if i == key else 0 for i in range(classes)])
                    else:
                        y.append(key)

                    # create a 400x400 sized power spectrogram, crop unnecessary white space
                    x.append(
                        get_visual_data(v_func=self.v_func, size=self.v_size, sr=self.sr,
                                        y=frame, bw=self.bw, hide_axes=True)
                    )
                    """
                    utils.data_to_image(rgb).show()
                    exit(0)
                    """

            x, y = np.array(x, dtype=Values.D_TYPE_IMG), np.array(
                y, dtype=Values.D_TYPE_IMG)
            yield x, y


class ChordProcessor(BatchProcessor):

    def __init__(self, chords, mix_dir, gen_dir="generated", mld=20, frame_length=1.0, n_load=10, ext_mix=".wav",
                 sr=44100, v_func=power_spectrogram, v_size=(256, 256), bw=True, noises=[], shift_range=range(0),
                 bits=16, map_file="mapping.pkl"):
        """
        Generate 'chords' of frame length 'frame_length' and mix them randomly with pre-loaded samples of
        audio files of length 'mld' located in 'mix_dir'. Chord will be generated in 'gen_dir' with extension '.wav'.
        Then a visualization function 'v_func' will be applied and the visualized data of 'v_size'
        is returned in batch sizes.

        :param chords: list, Chords to generate all modifications from
        :param gen_dir: str, directory where chords will be generated
        :param mix_dir: str, directory containing arbitrary music files which will be mixed with chord samples or None
        :param mld: float, duration [seconds] each mix file preload before sampling from it
        :param frame_length: float, length of each frame/batch in seconds
        :param n_load: int, number of randomly opened arbitrary files for mixing with chords
        :param ext_mix: str, extension of mix files '.wav' or '.mp3' ...
        :param sr: int, sampling rate of read chords and mix files
        :param v_func: function, visualization function in core.util.visualize
        :param v_size: (width, height), size of the visualized audio image
        :param bw: bool, if true generated image will be gray scale
        """
        self.mix_dir = mix_dir
        self.ext_mix = ext_mix
        self.mld = mld
        self.sr = sr
        self.v_func = v_func
        self.v_size = (v_size[0] / dpi, v_size[1] / dpi)
        self.bw = bw

        self._chords = []
        # Generate all chords used in this network
        if map_file and exists(map_file):
            print('loading pickle')
            with open(map_file, "rb") as handler:
                self._chords = pickle_load(handler)
        else:
            print("get all chord modifications")
            self._chords = self.get_all_chord_modifications(chords, gen_dir, shift_range, noises, bits=bits,
                                                            duration=frame_length, sr=sr)
            pickle.dump(self._chords, open(map_file, "wb"))
            print('dumping pickle')
        '''
        for i in range(len(chords)):
            self._chords.append(chords[i].generate(output_dir=gen_dir, extension=".wav", duration=frame_length))
        '''
        self.n_load = n_load
        self.frame_length = frame_length
        self.fgs = self._get_frame_generators()

    def get_classes(self):
        return list(self._chords.keys())

    def get_num_classes(self):
        return len(list(self._chords.keys()))

    @staticmethod
    def get_all_chord_modifications(chords, output_dir, shift_range, noises, bits=16, duration=1.0, sr=44100):
        def gen_real(_chord):
            return _chord.generate(output_dir=output_dir, extension=".wav", duration=duration, sr=sr, bits=bits,
                                   noise=None, freq_shift=0)

        def get_shift(_chord, _shift):
            return _chord.generate(output_dir=output_dir, extension="-shift%5f.wav" % _shift, duration=duration,
                                   sr=sr, bits=bits, noise=None, freq_shift=_shift)

        def get_real_with_noise(_chord, noise):
            return _chord.generate(output_dir=output_dir, extension="%s-.wav" % noise.__class__.__name__,
                                   duration=duration, sr=sr, bits=bits, noise=noise, freq_shift=0)

        def get_real_with_noise_and_shift(_chord, _noise, _shift):
            return _chord.generate(output_dir=output_dir,
                                   extension="-%s-shift%5f.wav" % (
                                       _noise.__class__.__name__, _shift),
                                   duration=duration, sr=sr, bits=bits, noise=_noise, freq_shift=_shift)

        mapping = {}
        for chord in tqdm.tqdm(chords, unit="chords"):
            mapping[chord.get_name()] = []
            mapping[chord.get_name()].append(gen_real(chord))
            logger.debug('generate noices of ', chord.get_name(), noises)
            for noise in noises:
                mapping[chord.get_name()].append(
                    get_real_with_noise(chord, noise))

            logger.debug('generate shift range of ',
                         chord.get_name(), shift_range)
            for shift in shift_range:
                mapping[chord.get_name()].append(get_shift(chord, shift))
                for noise in noises:
                    mapping[chord.get_name()].append(
                        get_real_with_noise_and_shift(chord, noise, shift))
        return mapping

    def _get_frame_generators(self):

        # Get data to modify original files
        if self.mix_dir:
            mix_files = utils.get_files_with_extension(
                self.mix_dir, extension=self.ext_mix)
            if len(mix_files) < self.n_load:
                raise ReaderException("You cannot load %s  files from %s, %s files where found. Please provide more files." % (str(self.n_load), self.mix_dir, str(len(mix_files))))

            # Generate num_load random indexes
            rand_idx = permutation([i for i in range(len(self.mix_dir))])[
                :self.n_load]

            # Load random mix files
            rand_mix_args = list(map(lambda x: (mix_files[x], self.sr, self.mld), rand_idx))
            mix_fgs = utils.parallize(AudioFrameGenerator, rand_mix_args)

        else:
            mix_fgs = None
        # Generate original data
        orig_fgs_map = ([
            (list(self._chords.keys()).index(name),
             AudioFrameGenerator(chord, self.sr, self.frame_length))
            for name in self._chords.keys() for chord in self._chords[name]])

        return [orig_fgs_map, mix_fgs]

    def get_next(self, test=False, one_hot=True, n_mixed_files=5,
                 rand_chord_sample=True, rand_mix_sample=True, rand_chord=True):

        classes = self.get_num_classes()
        idxs = len(self.fgs[0])
        o_index = -1

        # Get Random Input Chord or
        if rand_chord:
            o_index = np.random.randint(idxs)
        else:
            o_index = (o_index + 1) % idxs

        (key, orig_fg) = self.fgs[0][o_index]
        if Values.DEBUG:
            pp("Use chord: " + str(key))

        for frame in orig_fg.get_frames(frame_length=self.frame_length, num_frames=1,
                                        randomize=rand_chord_sample):

            if one_hot:
                y = [1 if c == key else 0 for c in range(classes)]
            else:
                y = key

            if self.fgs[1]:
                # choose audio files which will be mixed with the original chord
                for i in range(n_mixed_files):

                    i = randint(0, len(self.fgs[1]) - 1)
                    if Values.DEBUG:
                        pp("Mix with file: " + str(i))
                    _x = np.array(self.fgs[1][i].get_frames(frame_length=self.frame_length, num_frames=1,
                                                            randomize=rand_mix_sample)[0],
                                  dtype=Values.D_TYPE_AUDIO)
                    frame += _x

            # create a 400x400 sized power spectrogram, crop unnecessary white space
            x = get_visual_data(frame, self.sr, self.v_size,
                                self.v_func, "", self.bw, True)
            x, y = np.array(x, dtype=Values.D_TYPE_IMG), np.array(
                y, dtype=Values.D_TYPE_IMG)

            yield x, y

    def batch_iterator(self, batch_size=64, test=False, one_hot=True, n_batches=5000, n_mixed_files=5,
                       rand_chord_sample=True, rand_mix_sample=True, rand_chord=True):
        """
        Returns the next batch needed for feeding into the network


        frame dimension: 1x22050 (for 1 second of audio)
        -> modify frame by overlaying samples
        -> generate visualization using v_func
        ->

        :param batch_size: int, number of batches
        :param test: bool, get test data
        :param one_hot: bool, make y one hot
        :param n_mixed_files: int, number of files mixed with input chord
        :param n_batches: int, number of batches in 1 epoch
        :param rand_chord_sample: bool, randomize chord input sample
        :param rand_mix_sample: bool, randomize mix file samples
        :param rand_chord: bool, randomize getting new chord or get them in order
        :param bw: bool, convert visualization to gray scale
        :return: x,y
        """
        classes = self.get_num_classes()
        idxs = len(self.fgs[0])
        o_index = -1

        from sox_chords.util.utils import parallize

        if Values.DEBUG:
            pp("Generating " + str(n_batches) + " batches")
        for batch_i in range(n_batches):
            x, y = [], []
            args = []
            while len(args) < batch_size:
                if len(args) % 5 == 0 and Values.DEBUG:
                    pp(str(len(args)) + " of " + str(batch_size))

                # Get Random Input Chord or
                if rand_chord:
                    o_index = np.random.randint(idxs)
                else:
                    o_index = (o_index + 1) % idxs

                (key, orig_fg) = self.fgs[0][o_index]
                if Values.DEBUG:
                    pp("Use chord: " + str(key))

                for frame in orig_fg.get_frames(frame_length=self.frame_length, num_frames=1,
                                                randomize=rand_chord_sample):

                    if one_hot:
                        y.append(
                            [1 if c == key else 0 for c in range(classes)])
                    else:
                        y.append(key)

                    if self.fgs[1]:
                        # choose audio files which will be mixed with the original chord
                        for i in range(n_mixed_files):

                            i = randint(0, len(self.fgs[1]) - 1)
                            if Values.DEBUG:
                                pp("Mix with file: " + str(i))
                            _x = np.array(self.fgs[1][i].get_frames(frame_length=self.frame_length, num_frames=1,
                                                                    randomize=rand_mix_sample)[0],
                                          dtype=Values.D_TYPE_AUDIO)
                            frame += _x

                    # create a 400x400 sized power spectrogram, crop unnecessary white space
                    args.append((frame, self.sr, self.v_size,
                                 self.v_func, "", self.bw, True))

            x = parallize(get_visual_data, args)
            x, y = np.array(x, dtype=Values.D_TYPE_IMG), np.array(
                y, dtype=Values.D_TYPE_IMG)

            yield x, y
