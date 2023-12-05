import argparse
from pathlib import Path

import nemo.collections.asr as nemo_asr
import torch
from whisper.normalizers import EnglishTextNormalizer

from src.differs import jiwer_differ
from src.transcript_test import TranscriptTest


class NemoTest(TranscriptTest):
    """
    Test to evaluate the difference between the model transcript and the target transcript
    """

    def __init__(
        self,
        model_name: str,
        model_class: str,
        language: str = None,
        gpu: int = 0,
        **kwargs,
    ):
        super().__init__(model_name, language, **kwargs)
        self.model_name = model_name
        self.model_class = model_class
        self.language = language

        model_cls = nemo_asr.models
        self.model = getattr(model_cls, model_class).from_pretrained(
            model_name, map_location=torch.device(f"cuda:{gpu}")
        )
        self.model.transcribe

        self.model_settings = {"channel_selector": "average", "batch_size": 1}

        self.normalizer = EnglishTextNormalizer()
        self.transcriber = self.model.transcribe
        self.differ = jiwer_differ

    def additional_info(self) -> dict:
        return {
            "modelName": f"{self.model_name} ({self.model_class})",
            "language": self.language,
            "modelSettings": str(self.model_settings),
        }

    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe the audio file by model and return the transcript

        Args:
            audio_path: path to audio file

        Returns:
            Transcript
        """
        results = self.transcriber([str(audio_path)], **self.model_settings)
        return results[0]

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
        differ_results["model_name"] = self.model_name

        return differ_results

    @staticmethod
    def subparser(subparser: argparse.ArgumentParser):
        """
        Add arguments to the subparser

        Args:
            subparser: parser to add arguments to
        """

        subparser.add_argument(
            "-m",
            "--model-type",
            type=str,
            dest="model_name",
            required=True,
        )

        subparser.add_argument(
            "-c", "--model-class", type=str, dest="model_class", required=True
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
