from __future__ import print_function
import tempfile
from sox_chords.util import visualize
from sox_chords.music.chords import triad
from sox_chords.music import utils
import librosa


def test_spectrograms():
    audio_dir = tempfile.mkdtemp()
    chord = triad.MajorTriad(utils.get_note("C", 4))
    output_path = chord.generate(output_dir=audio_dir)

    y, sr = librosa.load(output_path)

    data = visualize.get_visual_data(y=y, sr=sr, v_func=visualize.mel_power_spectrogram, bw=True, size=(25.6, 25.6), hide_axes=True)
    data = visualize.get_visual_data(y=y, sr=sr, v_func=visualize.power_spectrogram, bw=False, size=(25.6, 25.6), hide_axes=True)
    data = visualize.get_visual_data(y=y, sr=sr, v_func=visualize.chromagram, bw=False, size=(25.6, 25.6), hide_axes=True)


if __name__ == "__main__":
    test_spectrograms()
