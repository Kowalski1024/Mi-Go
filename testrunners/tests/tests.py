import argparse
from pathlib import Path

import torch
import numpy as np
import whisper
from whisper.normalizers import EnglishTextNormalizer

from testrunners.tests import TranscriptTest
from libs.differs import jiwer_differ
import databases


class TranscriptDifference(TranscriptTest):
    """
    Test to evaluate the difference between the model transcript and the target transcript
    """

    def __init__(self, model_type: str, model_language: str = None, gpu: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.model_type = model_type
        self.model_language = model_language
        self.model = whisper.load_model(model_type, device=torch.device(f"cuda:{gpu}"))

        self.normalizer = EnglishTextNormalizer()
        self.transcriber = self.model.transcribe
        self.differ = jiwer_differ

    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe the audio file by model and return the transcript

        Args:
            audio_path: path to audio file

        Returns:
            Transcript
        """

        results = self.transcriber(audio=str(audio_path), verbose=False, language=self.model_language)
        self.language = results["language"]

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

        differ_results = jiwer_differ(normalized_model, normalized_target)
        differ_results["detectedLanguage"] = self.language

        return differ_results

    def testplan_postprocess(self, testplan):
        """
        Add model type to the testplan

        Args:
            testplan: testplan to postprocess
        """
        # calculate var and mean
        wer = np.array([video["results"]["wer"] for video in testplan["items"] if "error" not in video["results"]])
        mean = np.mean(wer)
        std = np.std(wer)

        testplan["model"] = {
            "name": self.model_type,
            "language": self.model_language,
            "werMean": mean,
            "werStd": std,
        }

        databases.insert_transcript_diff_results(testplan, self.differ)

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

        gpus = torch.cuda.device_count()

        subparser.add_argument(
            "-g",
            "--gpu",
            type=int,
            dest="gpu",
            choices=range(gpus),
            default=0,
            help=f"GPU to use (default: 0, max: {gpus - 1})",
        )

        subparser.add_argument(
            "-ml",
            "--model-language",
            type=str,
            dest="model_language",
            default=None,
            required=False,
            help=f"Model language (default: None)"
        )
