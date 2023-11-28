import argparse
import json
import pathlib

from databases import insert_transcript_diff_results
from libs.differs import jiwer_differ


def db_from_files(files):
    """
    Insert the testplan into the database

    Args:
        files: list of files to insert
    """
    for file in files:
        with open(file, encoding="utf8") as f:
            testplan = json.load(f)
        insert_transcript_diff_results(testplan, jiwer_differ)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, help="Directory with testplans")
    args = parser.parse_args()

    files = [str(path) for path in pathlib.Path(args.directory).glob("*.json")]

    db_from_files(files)
