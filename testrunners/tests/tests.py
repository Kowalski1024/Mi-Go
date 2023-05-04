import argparse
from pathlib import Path

import whisper
from whisper.normalizers import EnglishTextNormalizer

from testrunners.tests import TranscriptTest
from libs.differs import differ
import databases


class TranscriptDifference(TranscriptTest):
    """
    Test to evaluate the difference between the model transcript and the target transcript
    """

    def __init__(self, model_type: str, **kwargs):
        super().__init__(**kwargs)
        self.model_type = model_type
        self.model = whisper.load_model(model_type)

        self.normalizer = EnglishTextNormalizer()
        self.transcriber = self.model.transcribe

    def transcribe(self, audio_path: Path, remove_audio=True) -> str:
        """
        Transcribe the audio file by model and return the transcript

        Args:
            audio_path: path to audio file
            remove_audio: whether to remove the audio file after transcribing

        Returns:
            Transcript
        """

        results = self.transcriber(audio=str(audio_path), verbose=False)
        self.language = results["language"]

        if remove_audio:
            audio_path.unlink()

        return results["text"]

    def compare(self, model_transcript, target_transcript) -> dict:
        """
        Compare the model transcript to the target transcript

        Args:
            model_transcript: transcript from the model
            target_transcript: transcript from the target

        Returns:
            dict with the results of the comparison
        """

        normalized_model = self.normalizer(model_transcript)
        normalized_target = self.normalizer(target_transcript)

        differ_results = differ(normalized_model, normalized_target)
        differ_results["detectedLanguage"] = self.language

        return differ_results

    def testplan_postprocess(self, testplan):
        """
        Add model type to the testplan

        Args:
            testplan: testplan to postprocess
        """

        testplan["model"] = {"name": self.model_type}

        databases.insert_transcript_diff_results(testplan)

    @staticmethod
    def subparser(subparser: argparse.ArgumentParser):
        """
        Add arguments to the subparser

        Args:
            subparser: parser to add arguments to
        """

        model_types = [
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "tiny.en",
            "base.en",
            "small.en",
            "medium.en",
        ]

        subparser.add_argument(
            "-m",
            "--model-type",
            type=str,
            dest="model_type",
            choices=model_types,
            required=True,
        )
