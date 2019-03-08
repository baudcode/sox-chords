
import pyaudio
import wave
from sox_chords.music.noise_reduction import noise
import librosa
import numpy as np
# sudo apt-get install portaudio19-dev
# sudo -H pip3 install pyaudio pysndfx
from sox_chords.util.visualize import RealTimePlot, get_visual_data, mel_power_spectrogram, power_spectrogram, chromagram, QtGui
from threading import Thread
from queue import Queue
from time import sleep
from functools import reduce
import imageio


class Record:

    def __init__(self, pyaudio_format=pyaudio.paFloat32, channels=1, sr=44100, chunk_size=1024, record_seconds=10, output_file=None):
        self.pyaudio_format = pyaudio_format
        self.channels = channels
        self.sr = sr
        self.chunk_size = chunk_size
        self.record_seconds = record_seconds
        self.output_file = output_file
        self.audio = pyaudio.PyAudio()
        for device in range(self.audio.get_device_count()):
            print(self.audio.get_device_info_by_index(device)['name'])
        print(self.audio.get_default_host_api_info(), self.audio.get_default_input_device_info())
        # open stream
        self.stream = self.audio.open(
            format=pyaudio_format, channels=channels, rate=sr, input=True, frames_per_buffer=chunk_size)

    @property
    def num_samples(self):
        return int(self.sr / self.chunk_size * self.record_seconds)

    def record(self, apply_noise_reduction=True, plot=True):
        samples = self.num_samples
        frames = []

        print('start recording')
        while True:
            frame = self.stream.read(self.chunk_size)
            out = np.fromstring(frame, dtype=np.float32)
            print(out.shape, out.dtype, out.max(), out.min())
            # if apply_noise_reduction:
            #    out = noise.reduce_noise_centroid_mb(out, self.sr)

            if self.output_file:
                frames.append(frame)

            yield out

        # stop Recording
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        if self.output_file:
            Wave.save(frames, self.output_file, self.channels,
                      self.pyaudio_format, self.sr)


class AudioAnalyser:

    @staticmethod
    def get_loudness(y):
        S = librosa.stft(y)**2
        power = np.abs(S)**2
        p_mean = np.sum(power, axis=0, keepdims=True)
        # or whatever other reference power you want to use
        p_ref = np.max(power)
        loudness = librosa.amplitude_to_db(p_mean, ref=p_ref)
        return loudness


class Wave:

    @staticmethod
    def load(filename):
        y, sr = librosa.load(filename)
        return y, sr

    @staticmethod
    def save(y, filename, channels, pyaudio_format, sr):
        waveFile = wave.open(filename, 'wb')
        waveFile.setnchannels(channels)
        waveFile.setsampwidth(audio.get_sample_size(pyaudio_format))
        waveFile.setframerate(sr)
        waveFile.writeframes(b''.join(y))
        waveFile.close()


should_stop = False


def create_spectrograms(data_queue, images_queue, sr=22050, n=30):

    while not should_stop:
        while data_queue.qsize() < n and not should_stop:
            sleep(0.00001)

        items = reduce(lambda x, y: x + y,
                       [data_queue.get() for i in range(n)])
        items = np.asarray(items, dtype=np.float)
        data_queue.task_done()
        data = get_visual_data(y=items, sr=44100, v_func=power_spectrogram, bw=False, size=(
            256, 256), hide_axes=True)
        images_queue.put(data)
        imageio.imsave("image.png", data)
        exit(0)
    print("create spectrograms end")


def record():
    r = Record()

    for y in r.record():
        pass
        # print(y.shape, y.max(), y.min())
        # queue.put(y)
        # print('new sample')
    should_stop = True
    print("should stop...")


def show_images(rtp, queue):
    while not should_stop:
        while queue.empty() and not should_stop:
            sleep(0.00001)
        item = queue.get()
        queue.task_done()
        rtp.update(item)


class Recorder:

    def __init__(self):
        self.r = Record()
        self.buffer = Queue(maxsize=self.r.num_samples)
        self.buffer_images = Queue(maxsize=self.r.num_samples)
        self.rtp = RealTimePlot("audio signal")

    def start(self):
        thread = Thread(target=record, args=(self.r, self.buffer, ))
        thread.start()

        thread2 = Thread(target=create_spectrograms,
                         args=(self.buffer, self.buffer_images))
        thread2.start()

        thread3 = Thread(target=show_images, args=(
            self.rtp, self.buffer_images))
        thread3.start()
        print("showing...")
        try:
            self.rtp.show()
            app.exec_()
            print("joining...")
            thread3.join()
        except Exception as e:
            app.exit()


if __name__ == '__main__':
    try:
        thread2 = Thread(target=record)
        thread2.daemon = True
        thread2.start()
        thread2.join()
    except Exception as e:
        thread2.terminate()
    # app = QtGui.QApplication([])
    # recorder = Recorder()
    # recorder.start()
