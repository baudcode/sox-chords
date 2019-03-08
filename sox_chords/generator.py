from sox_chords.util.processors import ChordProcessor
from sox_chords.util.sox import WhiteNoise, BrownNoise, TpdfNoise
from sox_chords.util.logger import logger
import os
import tempfile
import numpy as np

import uuid


def generate(chords, out_dir):

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for name in [c.get_name().lower() for c in chords]:
        if not os.path.exists(os.path.join(out_dir, name)):
            os.makedirs(os.path.join(out_dir, name))

    for chord in chords:
        chord.generate(output_dir=os.path.join(
            out_dir, chord.get_name().lower()), extension="%s.wav" % uuid.uuid4())


def get_generator(chords, gen_dir=tempfile.mkdtemp(), bw=False, noices=[WhiteNoise(), BrownNoise(), TpdfNoise()],
                  shift_range=np.arange(-0.5, 0.5, 0.1), v_size=(128, 128)):

    dp = ChordProcessor(chords, None, gen_dir, v_size=v_size, bw=bw, noises=noices, shift_range=shift_range)

    def generator():
        while 1:
            for x, y in dp.get_next():
                x = x / 255.
                x = (x - x.mean()) / (x.std() + 1e-9)
                # print(batch_y)
                # print("image", x.shape, y.shape, x.dtype, y.dtype)
                yield x, y

    return generator
