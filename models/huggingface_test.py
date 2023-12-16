import argparse
from pathlib import Path

import torch
from transformers.pipelines import AutomaticSpeechRecognitionPipeline

from src.differs import jiwer_differ
from src.transcript_test import TranscriptTest


class HugginfaceTest(TranscriptTest):
    """
    Test to evaluate the difference between the model transcript and the target transcript
    """

    def __init__(
        self,
        model_name: str,
        language: str,
        chunk_length_s: int,
        stride_length_s: tuple[int, int] = (4, 2),
        config: str = None,
        tokenizer: str = None,
        feature_extractor: str = None,
        decoder: str = None,
        gpu: int = 0,
        **kwargs,
    ):
        super().__init__(model_name, language, **kwargs)
        self.model_name = model_name
        self.language = language
        self.chunk_length_s = chunk_length_s
        self.stride_length_s = stride_length_s
        self.config = config
        self.tokenizer = tokenizer
        self.feature_extractor = feature_extractor
        self.decoder = decoder

        self.model = AutomaticSpeechRecognitionPipeline(
            model=model_name,
            tokenizer=tokenizer,
            feature_extractor=feature_extractor,
            config=config,
            device=gpu,
        )
        self.transcriber = self.model
        self.differ = jiwer_differ

    def additional_info(self) -> dict:
        model_settings = {
            "chunk_length_s": self.chunk_length_s,
            "stride_length_s": self.stride_length_s,
            "config": self.config,
            "tokenizer": self.tokenizer,
            "feature_extractor": self.feature_extractor,
            "decoder": self.decoder,
        }

        return {
            "modelName": f"{self.model_name} ({self.model_class})",
            "language": self.language,
            "modelSettings": str(model_settings),
        }

    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe the audio file by model and return the transcript

        Args:
            audio_path: path to audio file

        Returns:
            Transcript
        """
        return self.model(
            audio_path,
            chunk_length=self.chunk_length_s,
            stride_length=self.stride_length_s,
        )["text"]

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
            "-m",
            "--model-type",
            type=str,
            dest="model_name",
            required=True,
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

        subparser.add_argument(
            "-c",
            "--chunk-length",
            type=int,
            dest="chunk_length_s",
            required=True,
            help=f"Chunk length in seconds",
        )

        subparser.add_argument(
            "-s",
            "--stride-length",
            type=int,
            nargs=2,
            dest="stride_length_s",
            default=(4, 2),
            required=False,
            help=f"Stride length in seconds (default: (4, 2))",
        )

        subparser.add_argument(
            "--config",
            type=str,
            dest="config",
            required=False,
            help=f"Config file",
        )

        subparser.add_argument(
            "--tokenizer",
            type=str,
            dest="tokenizer",
            required=False,
            help=f"Tokenizer file",
        )

        subparser.add_argument(
            "--feature-extractor",
            type=str,
            dest="feature_extractor",
            required=False,
            help=f"Feature extractor file",
        )

        subparser.add_argument(
            "--decoder",
            type=str,
            dest="decoder",
            required=False,
            help=f"Decoder file",
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
