from pathlib import Path

import databases
from libs.differs import jiwer_differ
from testrunners.transcript_test import TranscriptTest


class DummyTest(TranscriptTest):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.language = "en"
        self.transcriber = lambda x: "This is a model for tests :)"
        self.normalizer = lambda x: x.lower()
        self.differ = jiwer_differ

    def transcribe(self, audio_path: Path) -> str:
        return self.transcriber(audio_path)

    def compare(self, model_transcript, target_transcript):
        normalized_model = self.normalizer(model_transcript)
        normalized_target = self.normalizer(target_transcript)

        differ_results = jiwer_differ(normalized_model, normalized_target)
        differ_results["detectedLanguage"] = self.language

        return differ_results

    def testplan_postprocess(self, testplan):
        testplan["model"] = {
            "name": "Dummy",
            "language": "en",
            "werMean": 0.0,
            "werStd": 1.0,
        }

    def insert_to_database(self, testplan):
        databases.insert_transcript_diff_results(testplan, self.differ)
