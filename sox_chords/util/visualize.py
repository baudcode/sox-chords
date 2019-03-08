from __future__ import print_function

from math import ceil
from os.path import basename, exists
from time import sleep, time
try:
    from PyQt4 import QtGui
    import pyqtgraph as pg
except ImportError as e:
    print("Warning: cannot import PyQt4. Unable to use RealTimePlot. When using virtualenv use --system-site-packages.")

import librosa
import numpy as np
import librosa.display as display

from sox_chords.exceptions import VisualizerException
from sox_chords.util.image import fig2data, plt


class Actions(object):
    SAVE_PLOT, SHOW, GET_DATA = range(3)


fig_size = (7, 5)
dpi = 10


def chromagram(y=None, sr=22050, title="", bw=False, hide_axes=False):
    """
    Visualizable function \n
    Create a chromagram using librosa.feature.chroma_cqt

        :param y: list, input data
        :param sr: int, sampling rate
        :param title: str, title of the plot
        :param subplot: subplot array [y,x,id] or null if no subplot should be used
        :param bw: bool, black and white coloured
        :param hide_axes: bool, hide title and axes
        :param crop: cropping box = (x_start, y_start, width, height)
        :return: null
    """

    y_harmonic, y_percussive = librosa.effects.hpss(y)
    # We'll use a CQT-based chromagram here.  An STFT-based implementation also exists in chroma_cqt()
    # We'll use the harmonic component to avoid pollution from transients
    c = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)

    # Display the chromagram: the energy in each chromatic pitch class as a function of time
    # To make sure that the colors span the full range of chroma values, set vmin and vmax
    if bw:
        librosa.display.specshow(
            c, sr=sr, x_axis='time', cmap='gray_r', y_axis='chroma', vmin=0, vmax=1)
    else:
        librosa.display.specshow(
            c, sr=sr, x_axis='time', y_axis='chroma', vmin=0, vmax=1)

    if not hide_axes:
        plt.title(title)
        plt.colorbar()
        plt.tight_layout()


def power_spectrogram(y=None, sr=22050, title="", bw=False, hide_axes=False):
    """
    Visualizable function \n
    Create a power spectrogram using np.aps(D) ** 2

        :param y: list, input data
        :param sr: int, sampling rate
        :param title: str, title of the plot
        :param bw: bool, black and white coloured
        :param hide_axes: bool, hide title and axes
        :return: null
    """
    d = librosa.stft(y)

    if bw:
        display.specshow(librosa.amplitude_to_db(np.abs(d) ** 2, ref=np.max), cmap='gray_r', sr=sr,
                         y_axis='log', x_axis='time')
    else:
        display.specshow(librosa.amplitude_to_db(
            np.abs(d) ** 2, ref=np.max), y_axis='log', x_axis='time')

    if not hide_axes:
        plt.title(title)
        plt.colorbar(format='%+2.0f dB')
        plt.tight_layout()


def mel_power_spectrogram(y=None, sr=22050, title="", bw=False, hide_axes=False):
    """
    Visualizable function \n
    Create a mel scale using librosa.melspectrogram

        :param y: list, input data
        :param sr: int, sampling rate
        :param title: str, title of the plot
        :param bw: bool, black and white coloured
        :param hide_axes: bool, hide title and axes
        :return: null
    """

    # Let's make and display a mel-scaled power (energy-squared) spectrogram
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)

    # Convert to log scale (dB). We'll use the peak power as reference.
    log_S = librosa.amplitude_to_db(S, ref=np.max)

    # Display the spectrogram on a mel scale
    # sample rate and hop length parameters are used to render the time axis
    if bw:
        librosa.display.specshow(
            log_S, sr=sr, cmap='gray_r', x_axis='time', y_axis='mel')
    else:
        librosa.display.specshow(log_S, sr=sr, x_axis='time', y_axis='mel')

    if not hide_axes:
        plt.title(title)
        plt.colorbar(format='%+02.0f dB')
        plt.tight_layout()


def show_images(imgs=None, titles=None, hide_axes=False, size=(70, 50)):
    if len(imgs) < 4:
        plot_x = len(imgs)
    else:
        plot_x = 4

    plot_y = int(ceil(float(len(imgs)) / float(plot_x)))
    if hide_axes:
        fig = plt.figure(frameon=False, dpi=dpi)
        fig.set_size_inches(size[0], size[1])
    else:
        fig = plt.figure(figsize=(size[0] / dpi, size[1] / dpi), dpi=dpi * 10)
        # fig.set_size_inches(size[0] / 10.0, size[1] / 10.0)
    for plot_id, img in enumerate(imgs):
        plt.subplot(plot_y, plot_x, plot_id + 1)
        if titles is not None:
            plt.title(titles[plot_id])
        plt.imshow(img, cmap='coolwarm')

    plt.show()


class ContinuousPlot:

    def __init__(self, count, smooth=True, figsize=(10, 10), max_per_row=4):
        self.interpolation = "sinc" if smooth else "nearest"
        if count <= max_per_row:
            self.fig, self.axes = plt.subplots(1, count, figsize=figsize)
        else:
            self.fig, self.axes = plt.subplots(
                (count // max_per_row) + 1, max_per_row, figsize=figsize)

        self.fig.subplots_adjust(hspace=0.1, wspace=0.1)

        plt.ion()

    def _plt_img(self, image, label, index):

        ax = self.axes.flat[index]
        ax.clear()
        ax.imshow(image / 255.0, interpolation=self.interpolation)
        ax.set_xlabel(label)

    def show(self, images, labels, pause=0.05):
        assert(len(images) == len(labels))

        for i in range(len(images)):
            self._plt_img(images[i], labels[i], i)

        for ax in self.axes.flat:
            ax.set_xticks([])
            ax.set_yticks([])

        plt.pause(pause)


try:
    class RealTimePlot(QtGui.QWidget):

        def __init__(self, title, parent=None):
            QtGui.QWidget.__init__(self, parent)
            self.setWindowTitle(title)
            layout = QtGui.QGridLayout()
            self.setLayout(layout)
            # adding image to layout
            self.plot = pg.ImageView()
            layout.addWidget(self.plot, 0, 0)

        def update(self, image):
            self.plot.setImage(image)
            self.plot.update()

        def update_image(self, queue, start_time, frame_rate_float):
            while not queue.empty():
                item = queue.get()
                print('got item')
                queue.task_done()
                for g, image in enumerate(item):
                    while (time() - start_time) < frame_rate_float:
                        sleep(0.00001)
                    self.plot.setImage(image)
                    self.plot.update()
                    # pg.QtGui.QApplication.processEvents()
                    start_time = time()
except NameError as e:
    print("warning cannot import realtime plot")
    # Warning: cannot define RealTimePlot because PyQt4 was not found
    pass


def _visualize(data=None, titles=None, sr=22050, size=(22.4, 16.5), v_func=None, out_file="out.png", action=0, bw=False,
               hide_axes=False):
    """
    Visualize data y
        :param data: list, array of [data array]
        :param sr: int, sampling rate
        :param v_func: func, visualizable function
        :param out_file: str, output file path
        :param size: tuple, (width, height) must be multiple of (7,5) and is actual_size / dpi (actual_size/ 10)
        :param action: AudioVisualizer.Action, what to do at the end
        :param hide_axes: bool, hide title and axes
        :return: RGBA data(4d np array), if action is GET_DATA, else None
    """
    if len(data) < 4:
        plot_x = len(data)
    else:
        plot_x = 4

    plot_y = int(ceil(float(len(data)) / float(plot_x)))

    if hide_axes:
        fig = plt.figure(frameon=False, dpi=dpi)
        fig.set_size_inches(size[0], size[1])
    else:
        fig = plt.figure(figsize=(size[0] / dpi, size[1] / dpi), dpi=dpi * 10)
        # fig.set_size_inches(size[0] / 10.0, size[1] / 10.0)

    if titles:
        if len(titles) != len(data):
            raise VisualizerException(
                "If you specify titles, please specify len(data) titles")

    for plot_id, y in enumerate(data):
        plt.subplot(plot_y, plot_x, plot_id + 1)
        if len(data) == 1 and hide_axes:
            # no axis and remove borders
            ax = plt.Axes(fig, [0., 0., 1., 1.])
            ax.set_axis_off()
            fig.add_axes(ax)

        v_func(y=y, sr=sr, title=titles[plot_id], bw=bw, hide_axes=hide_axes)

    _data = None
    if action == Actions.SHOW:
        plt.show()

    elif action == Actions.SAVE_PLOT:
        if hide_axes:
            plt.savefig(out_file, dpi=dpi)
        else:
            plt.savefig(out_file)
    else:
        _data = fig2data(fig, bw=bw, crop=None)
    plt.close(fig)
    return _data


def get_visual_data(y=None, sr=22050, size=(22.4, 16.0), v_func=None, title="title", bw=True, hide_axes=True):
    """

    :param y: list of samples, input data
    :param sr: int, sampling rate
    :param v_func: func, visualizable function
    :param title: str, title of the image
    :param size: size of the histogram
    :param bw: bool, black and white indicator
    :param hide_axes: bool, hide title and axes
    :param crop: (left, upper, right, lower)
    :return: x,y: tuple of image data
    """
    return _visualize(data=[y], sr=sr, size=size, v_func=v_func, titles=[title], action=Actions.GET_DATA, bw=bw,
                      hide_axes=hide_axes)


def visualize(y=None, sr=22050, size=(224, 160), v_func=None, out_file="out.png", title="title", show=True, bw=False,
              hide_axes=False):
    _visualize(data=[y], sr=sr, size=size, v_func=v_func, out_file=out_file, titles=[title], action=int(show),
               bw=bw, hide_axes=hide_axes)


def visualize_audio_files(v_func=None, sr=22050, size=(22.4, 16.5), audio_files=None, out_file="out.png", show=True,
                          bw=False, hide_axes=False):
    _size = (size[0] * 10, size[1] * 10)

    if not hide_axes and (_size[0] % fig_size[0] != 0 or _size[1] % fig_size[1] != 0):
        raise VisualizerException("Wrong width/height ratio: current: {}, needed: {} or {}:{}".
                                  format(float(_size[0]) / _size[1], float(fig_size[0]) / fig_size[1], fig_size[0],
                                         fig_size[1]))

    """
    Visualize multiple audio files using a histogram function defined in AudioVisualizer

    :param v_func: func, visualizable function
    :param sr: int, sampling rate
    :param audio_files: list, array of audio files
    :param out_file: str, output file name
    :param size: size of hole picture
    :param show: bool, show (true) or save (false)
    :param bw: bool, image to grayscale
    :param hide_axes: hide the axes and make everything compact
    :return: none
    """
    data = []
    titles = [basename(_file) for _file in audio_files]
    for audio_file in audio_files:
        y, sr = librosa.load(path=audio_file, sr=sr)
        data.append(y)

    _visualize(data=data, titles=titles, size=size, v_func=v_func, sr=sr, out_file=out_file, action=int(show), bw=bw,
               hide_axes=hide_axes)


if __name__ == "__main__":

    in_dir = "../../chords/"

    from os import listdir
    from os.path import join
    from sox_chords.util.image import show_image

    files = sorted([join(in_dir, file)
                    for file in listdir(in_dir) if file.endswith(".wav")])
    print(files)
    print("Plotting: ", files[:5])

    visualize_audio_files(audio_files=files[:4], v_func=mel_power_spectrogram, size=(
        70, 50), hide_axes=True, show=True)
    # visualize_audio_files(audio_files=files[:8], v_func=power_spectrogram, size=(25.6, 25.6), hide_axes=False, bw=True, show=False)

    y, sr = librosa.load(files[0])
    data = get_visual_data(y=y, sr=sr, v_func=mel_power_spectrogram,
                           bw=True, size=(25.6, 25.6), hide_axes=True)
    show_image(data)
    data = get_visual_data(y=y, sr=sr, v_func=power_spectrogram,
                           bw=False, size=(25.6, 25.6), hide_axes=True)
    show_image(data)
    data = get_visual_data(y=y, sr=sr, v_func=chromagram,
                           bw=False, size=(25.6, 25.6), hide_axes=True)
    show_image(data)

    """
    visualize_audio_files(v_func=mel_power_spectrogram,
                              audio_files=files[:16], out_file="mel_power_spectrogram.png", show=False, hide_axes=True)
    visualize_audio_files(v_func=chromagram,
                              audio_files=files[:16], out_file="chromagram.png", show=True)
    """
