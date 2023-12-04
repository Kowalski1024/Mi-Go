import argparse
from pathlib import Path
from typing import Callable, Optional


class TranscriptTest:
    """
    Base class for transcript tests, all transcript tests should inherit from this class
    """

    def __init__(self, model_name: str, language: str, **kwargs):
        # transcriber is a function that takes a path to an audio file and returns a transcript
        # should be provided by the model
        self.transcriber: Optional[Callable] = None

        # normalizer is a function that takes a transcript and returns a normalized transcript
        # see libs/normalizers.py for examples
        self.normalizer: Optional[Callable] = None
        self.language: str = language
        self.model_name: str = model_name

    def additional_info(self) -> dict:
        """
        Override this method, should return additional info about the test

        Returns:
            dict with additional info
        """
        return {
            "modelName": self.model_name,
            "language": self.language,
        }

    @staticmethod
    def subparser(subparser: argparse.ArgumentParser):
        """
        Use this method to add arguments to the subparser

        Args:
            parser: parser to add arguments to
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
