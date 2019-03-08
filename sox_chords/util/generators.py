from os.path import join, basename, exists

from pickle import load as pickle_load
from pickle import dump as pickle_dump
from librosa import load as librosa_load
from librosa import get_duration
from random import randint

from sox_chords.values import Values
from sox_chords.util.logger import pp
from sox_chords.exceptions import GeneratorException


class AudioFrameGenerator(object):

    def __init__(self, input_file="", sr=22050, load_duration=5.0):
        """

        :param input_file: str, input audio file
        :param sr: int, sampling rate
        :param load_duration: float, duration in seconds to load samples from an audio file in advance
        """
        self.load_duration = load_duration
        self.input_file = input_file
        self.sr = sr
        self._load()

    def _load_file_raw(self, pkl):
        self.y, self.sr = librosa_load(path=self.input_file, sr=self.sr, duration=self.load_duration)
        if Values.USE_PKL:
            pickle_dump([self.y, self.sr], open(pkl, "wb"))

    def _load(self):
        pkl = self.input_file + ".pkl"
        if exists(pkl) and Values.USE_PKL:
            self.y, self.sr = pickle_load(open(pkl, "rb"))
            if self.load_duration != (len(self.y) / self.sr):
                self._load_file_raw(pkl)

                if Values.DEBUG:
                    pp("Reloaded because durations do not match")

            else:
                if Values.DEBUG:
                    pp("Loaded PKL: " + pkl)
        else:
            self._load_file_raw(pkl)
            if Values.DEBUG:
                pp("Loaded Direct: " + basename(self.input_file))

        self.duration = get_duration(y=self.y, sr=self.sr)

    def get_frames(self, frame_length=1, num_frames=-1, randomize=False):
        """
        Get frames from an audio file

        :raise GeneratorException
        :param frame_length: frame length in seconds
        :param num_frames: if > 0 number of frames, else hole frame
        :param randomize: randomize the frame index otherwise it returns in order
        :return: list, list of frames length sampling_rate * frame_length
        """
        num_samples = int(frame_length * self.sr)
        if num_samples > len(self.y):
            raise GeneratorException("Cannot get %d  samples from %s  which contains only %d samples" % (num_samples, self.input_file, len(self.y)))

        _frames = []
        if num_frames < 0:
            num_frames = int(len(self.y) // num_samples)

        _i = -1
        while len(_frames) < num_frames:
            if randomize:
                _i = randint(0, num_frames - 1)
            else:
                _i += 1
            _frame = self.y[(_i * num_samples) %
                            len(self.y):((_i + 1) * num_samples) % (len(self.y) + 1)]

            if len(_frame) != 0:
                _frames.append(_frame)

        return _frames


def check_files_loadable(_path="", _sr=22050):
    from os import listdir, remove
    from os.path import join
    from sox_chords.util.utils import parallize
    """ Check that all files can be read by librosa"""
    def check_file(in_path=""):
        try:
            librosa_load(path=in_path, sr=_sr)
        except Exception as e:
            remove(in_path)
            pp("Delete: " + basename(in_path))

    files = [join(_path, _file) for _file in listdir(_path)]
    """ Check files now"""
    for i in range(0, len(files), 8):
        if i + 8 > len(files):
            _files = files[i:len(files)]
        else:
            _files = files[i:(i + 8)]
        print("Check: " + str(i))
        parallize(check_file, _files)

    return [join(_path, _file) for _file in listdir(_path)]


if __name__ == "__main__":

    """ HOW TO:
    from os import listdir, remove
    from os.path import join
    from AudioVisualizer import AudioVisualizer
    from Utils import Utils

    sr = 22050
    path = "/mnt/data/NewDownloads/audio/"
    files = [join(path, _file) for _file in listdir(path)]

    audio_path = files[randint(0, len(files) - 1)]
    generator = AudioFrameGenerator(input_file=audio_path, sr=sr)
    frames = generator.get_frames(frame_length=1, num_frames=-1)
    AudioVisualizer._visualize(hist_func=AudioVisualizer.power_spectrogram, data=frames[:16], sr=generator.sr, show=True)

    """
