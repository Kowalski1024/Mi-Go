import argparse
from pathlib import Path

import numpy as np
import torch
import whisper
from whisper.normalizers import EnglishTextNormalizer

from src.differs import jiwer_differ
from src.transcript_test import TranscriptTest


class WhisperTest(TranscriptTest):
    """
    Test to evaluate the difference between the model transcript and the target transcript
    """

    def __init__(self, model_name: str, language: str = None, gpu: int = 0, **kwargs):
        super().__init__(model_name, language, **kwargs)
        self.model_name = model_name
        self.language = language
        self.model = whisper.load_model(model_name, device=torch.device(f"cuda:{gpu}"))

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

        results = self.transcriber(
            audio=str(audio_path), verbose=False, language=self.language, fp16=False,
        )

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

    @staticmethod
    def subparser(subparser: argparse.ArgumentParser):
        """
        Add arguments to the subparser

        Args:
            subparser: parser to add arguments to
        """

        subparser.add_argument(
            "-m", "--model-type", type=str, dest="model_name", required=True,
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
            "-l",
            "--language",
            type=str,
            dest="language",
            default=None,
            required=False,
            help=f"Model language (default: None)",
        )
