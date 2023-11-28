import argparse
from pathlib import Path
from typing import Callable, Optional


class TranscriptTest:
    """
    Base class for transcript tests, all transcript tests should inherit from this class
    """

    def __init__(self, **kwargs):
        # transcriber is a function that takes a path to an audio file and returns a transcript
        # should be provided by the model
        self.transcriber: Optional[Callable] = None

        # normalizer is a function that takes a transcript and returns a normalized transcript
        # see libs/normalizers.py for examples
        self.normalizer: Optional[Callable] = None
        self.language: str = "en"

    @staticmethod
    def subparser(subparser: argparse.ArgumentParser):
        """
        Use this method to add arguments to the subparser

        Args:
            parser: parser to add arguments to
        """
        pass

    def testplan_postprocess(self, testplan: dict):
        """
        Use this method to postprocess the testplan, for example to add more details to the testplan

        Args:
            testplan: testplan to postprocess
        """
        pass

    def insert_to_database(self, testplan: dict):
        """
        Use this method to insert the testplan to the database

        Args:
            testplan: testplan to insert
        """
        pass

    def transcribe(self, audio_path: Path) -> str:
        """
        Override this method, should transcribe the audio file and return the transcript

        Args:
            audio_path: path to audio file

        Returns:
            Transcript
        """
        raise NotImplementedError

    def compare(self, model_transcript, target_transcript):
        """
        Override this method, should compare the model transcript to the target transcript

        Args:
            model_transcript: transcript from the model
            target_transcript: transcript from the target

        Returns:
            Results of the comparison
        """
        raise NotImplementedError
