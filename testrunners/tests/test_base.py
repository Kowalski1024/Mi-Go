from typing import Optional, Callable
import argparse
from pathlib import Path


class TranscriptTestBase:
    def __init__(self, **kwargs):
        self.transcriber: Optional[Callable] = None
        self.normalizer: Optional[Callable] = None
        self.language: str = 'en'

    @staticmethod
    def subparser(subparser: argparse.ArgumentParser):
        pass

    def testplan_postprocess(self, testplan):
        pass

    def transcribe(self, audio_path: Path, remove_audio=True) -> str:
        raise NotImplementedError

    def compare(self, model_transcript, target_transcript):
        raise NotImplementedError
