from pathlib import Path

from src.differs import jiwer_differ
from src.transcript_test import TranscriptTest


class DummyTest(TranscriptTest):
    def __init__(self, model_name: str = "DummyTest", **kwargs):
        super().__init__(model_name, language=None, **kwargs)

        self.language = "en"
        self.model_name = model_name
        self.transcriber = lambda x: "This is a model for tests :)"
        self.normalizer = lambda x: x.lower()
        self.differ = jiwer_differ

    def transcribe(self, audio_path: Path) -> str:
        return self.transcriber(audio_path)

    def compare(self, model_transcript, target_transcript):
        normalized_model = self.normalizer(model_transcript)
        normalized_target = self.normalizer(target_transcript)

        differ_results = jiwer_differ(normalized_model, normalized_target)

        return differ_results
