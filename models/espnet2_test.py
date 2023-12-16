import argparse
import os
from pathlib import Path

import soundfile
import torch
from espnet2.bin.asr_inference import Speech2Text
from espnet_model_zoo.downloader import ModelDownloader
from pydub import AudioSegment
from whisper.normalizers import EnglishTextNormalizer

from src.differs import jiwer_differ
from src.transcript_test import TranscriptTest


class Espnet2Test(TranscriptTest):
    """
    Test to evaluate the difference between the model transcript and the target transcript
    """

    def __init__(self, model_name: str, language: str, gpu: int = 0, **kwargs):
        super().__init__(model_name, language, **kwargs)
        self.model_name = model_name
        self.language = language

        downloader = ModelDownloader()
        # "Shinji Watanabe/librispeech_asr_train_asr_transformer_e18_raw_bpe_sp_valid.acc.best"
        self.model = Speech2Text(
            **downloader.download_and_unpack(self.model_name), device=f"cuda:{gpu}"
        )

        self.normalizer = EnglishTextNormalizer()
        self.transcriber = self.model
        self.differ = jiwer_differ

    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe the audio file by model and return the transcript

        Args:
            audio_path: path to audio file

        Returns:
            Transcript
        """
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        aduio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)

        # Split audio into chunks to avoid memory issues
        chunk_length_ms = 10 * 1000  # in milliseconds
        chunks = [
            audio[i : i + chunk_length_ms]
            for i in range(0, len(audio), chunk_length_ms)
        ]

        # Transcribe each chunk
        transcripts = []
        for i, chunk in enumerate(chunks):
            # Save chunk to a temporary file
            chunk_path = f"{audio_path.stem}_chunk{i}.wav"
            chunk.export(chunk_path, format="wav")

            # Load chunk
            audio, _ = soundfile.read(chunk_path)

            # Transcribe chunk
            nbests = self.transcriber(audio)
            results, *_ = nbests[0]

            transcripts.append(results.lower())

            # remove temporary file
            os.remove(chunk_path)

        # Join transcripts
        transcript = " ".join(transcripts)

        return transcript

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
