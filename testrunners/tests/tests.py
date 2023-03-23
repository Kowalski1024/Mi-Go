import argparse
from pathlib import Path

import whisper
from whisper.normalizers import EnglishTextNormalizer

from testrunners.tests import TranscriptTestBase
from lib.differs import differ
import db


class TranscriptDifference(TranscriptTestBase):
    def __init__(self, model_type: str, **kwargs):
        super().__init__(**kwargs)
        self.model_type = model_type
        self.model = whisper.load_model(model_type)

        self.normalizer = EnglishTextNormalizer()
        self.transcriber = self.model.transcribe

    def transcribe(self, audio_path: Path, remove_audio=True):
        results = self.transcriber(audio=str(audio_path), verbose=False)
        self.language = results['language']

        if remove_audio:
            audio_path.unlink()

        return results['text']

    def compare(self, model_transcript, target_transcript):
        normalized_model = self.normalizer(model_transcript)
        normalized_target = self.normalizer(target_transcript)

        differ_results = differ(normalized_model, normalized_target)
        differ_results['detectedLanguage'] = self.language

        return differ_results

    def testplan_postprocess(self, testplan):
        testplan['model'] = {
            'name': self.model_type
        }

        db.insert_transcript_diff_results(testplan)

    @staticmethod
    def subparser(subparser: argparse.ArgumentParser):
        model_types = ['tiny', 'base', 'small', 'medium', 'large', 'tiny.en', 'base.en', 'small.en', 'medium.en']

        subparser.add_argument('-m', '--model-type',
                               type=str, dest='model_type', choices=model_types, required=True
                               )
