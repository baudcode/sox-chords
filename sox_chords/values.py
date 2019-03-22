import numpy as np


class Values(object):

    EXTRACTED_FOLDER = "extracted"
    MAX_SEMI_TONES = 12
    MAX_CORE_NOTES = 7
    MAX_OCTAVES = 8
    MAX_NUM_KEYS = 12 * 8
    MAX_PARALLEL_THREADS = 8

    IS_NEXT_CORE_SEMI_TONE = [1, 3, 4, 6, 8, 10, 11]
    SEMI_TONE_STEPS = [2, 2, 1, 2, 2, 2, 1]
    MAJOR_SEMI_TONE_STEPS = [2, 2, 1, 2, 2, 2, 1]
    MINOR_SEMI_TONE_STEPS = [2, 1, 2, 2, 1, 2, 2]
    DEBUG = False
    CORE_NOTES = [
        "C", "D", "E", "F", "G", "A", "B"
    ]
    D_TYPE_AUDIO = np.uint32
    D_TYPE_IMG = np.uint8
    USE_PKL = True

    SUPPORTED_VIDEO_EXTENSIONS = ["mp4", "mpeg", "mpg", "avi", "mkv", "flv"]
    SUPPORTED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "jp2"]

    FFMPEG_PRESETS = ["ultrafast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]
