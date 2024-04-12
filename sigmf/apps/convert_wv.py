# Copyright: Multiple Authors
#
# This file is part of SigMF. https://github.com/sigmf/sigmf-python
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""converter for wv containers"""

import os
import tempfile
import datetime
import pathlib
import argparse
import getpass

from scipy.io import wavfile

from .. import archive
from ..sigmffile import SigMFFile
from ..utils import get_data_type_str


def convert_wv(input_wv_filename, archive_filename=None, start_datetime=None, author=None):
    """
    read a .wv and write a .sigmf archive
    """
    samp_rate, wav_data = wavfile.read(input_wv_filename)

    global_info = {
        SigMFFile.AUTHOR_KEY: getpass.getuser() if author is None else author,
        SigMFFile.DATATYPE_KEY: get_data_type_str(wav_data),
        SigMFFile.DESCRIPTION_KEY: f"Converted from {input_wv_filename}",
        SigMFFile.NUM_CHANNELS_KEY: 1 if len(wav_data.shape) < 2 else wav_data.shape[1],
        SigMFFile.RECORDER_KEY: os.path.basename(__file__),
        SigMFFile.SAMPLE_RATE_KEY: samp_rate,
    }

    if start_datetime is None:
        fname = pathlib.Path(input_wv_filename)
        mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime)
        start_datetime = mtime.isoformat() + "Z"

    capture_info = {SigMFFile.START_INDEX_KEY: 0}
    if start_datetime is not None:
        capture_info[SigMFFile.DATETIME_KEY] = start_datetime

    tmpdir = tempfile.mkdtemp()
    sigmf_data_filename = input_wv_filename + archive.SIGMF_DATASET_EXT
    sigmf_data_path = os.path.join(tmpdir, sigmf_data_filename)
    wav_data.tofile(sigmf_data_path)

    meta = SigMFFile(data_file=sigmf_data_path, global_info=global_info)
    meta.add_capture(0, metadata=capture_info)

    if archive_filename is None:
        archive_filename = os.path.basename(input_wv_filename) + archive.SIGMF_ARCHIVE_EXT
    meta.tofile(archive_filename, toarchive=True)
    return os.path.abspath(archive_filename)


def main():
    """
    entry-point for sigmf_convert_wv
    """
    parser = argparse.ArgumentParser(description="Convert .wv to .sigmf container.")
    parser.add_argument("input", type=str, help="wv file path")
    parser.add_argument("--author", type=str, default=None, help=f"set {SigMFFile.AUTHOR_KEY} metadata")
    args = parser.parse_args()

    out_fname = convert_wv(
        input_wv_filename=args.input,
        author=args.author,
    )
    print("Wrote", out_fname)


if __name__ == "__main__":
    main()
