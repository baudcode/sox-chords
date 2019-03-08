from argparse import ArgumentParser

from sox_chords.util.utils import _call_for_ret_code, get_files_with_extension
from os.path import exists, join, isdir, dirname, basename
from os import makedirs, listdir
from tqdm import trange
# ffmpeg -i input.flv -f s16le -acodec pcm_s16le output.raw


def convert(inputs, outputs):
    args = ["ffmpeg", "-y", "-i", inputs, "-ar", "16000", "-acodec", "pcm_s16le", outputs]
    return _call_for_ret_code(args, silent=False)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("-i", "--inputs", type=str, help="input directory", required=True)
    parser.add_argument("-o", "--outputs", type=str, help="output directory", required=True)
    args = parser.parse_args()

    files = get_files_with_extension(args.inputs, ".wav")
    print("Found %d wav files" % len(files))

    # create directory structure
    dirs = [name for name in listdir(args.inputs) if isdir(join(args.inputs, name))]
    print("Directories: ", dirs)

    print("Creating directories")
    for d in dirs:
        output_dir = join(args.outputs, d)
        if not exists(output_dir):
            makedirs(output_dir)

    for i in trange(len(files)):
        f = files[i]
        _dirname = basename(dirname(f))
        filename = basename(f)
        outputs = join(join(args.outputs, _dirname), filename)
        convert(f, outputs)
