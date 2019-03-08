import matplotlib.pyplot as plt
from sox_chords import values

# from random import randint

import numpy as np
from PIL import Image


import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['axes.titlesize'] = 8
matplotlib.rcParams['axes.labelsize'] = 5
matplotlib.rcParams['xtick.labelsize'] = 5
matplotlib.rcParams['ytick.labelsize'] = 5


def data_to_image(data=None):
    """
    Save data as image.tif
        :param data: rgb or gray scale data
        :return: PIL Image
    """
    im = Image.fromarray(data)
    if im.mode != 'RGB':
        im = im.convert('RGB')
    return im


def rgb2gray(rgb):
    """
    Convert
    :param rgb: np.array[3], red, green, blue
    :return: np.array[1]
    """
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])


def show_image(data=None):
    """
    Show an image with image magick

    :param data: str (path to image) or np.array representation of image
    :return: None
    """
    if type(data) == str:
        Image.open(data).show()
    else:
        _show_image(data_to_image(data))


def _show_image(img):
    plt.imshow(img)
    plt.show()


def fig2data(fig=None, bw=True, crop=None):
    """
        Convert figure to rgb or gray scale np array

        :param fig: matplotlib figure
        :param bw: bool, true only returns 1 channel (black and white)
        :param crop: (left, upper, right, lower)
        :return rgb (np.array[h][w][3]) or gray scale(np.array[h][w]) if bw is true
    """
    # draw the renderer
    fig.canvas.draw()

    # Get the GBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_rgb(), dtype=values.Values.D_TYPE_IMG)
    buf.shape = (h, w, 3)
    if bw:
        buf = rgb2gray(buf)
    if crop:
        buf = np.asarray(data_to_image(buf).crop(box=crop), dtype=values.Values.D_TYPE_IMG)

    return buf
