import unittest
from unittest import mock
from pathlib import Path

from models.dummy_test import DummyTest

class TestDummyTest(unittest.TestCase):
    def setUp(self):
        self.dummy_test = DummyTest()

    @mock.patch('src.differs.jiwer_differ')
    def test_transcribe(self, mock_differ):
        mock_differ.return_value = {'wer': 0.0, 'mer': 0.0}

        audio_path = Path("path/to/audio.wav")
        result = self.dummy_test.transcribe(audio_path)

        self.assertEqual(result, "This is a model for tests :)")

    def test_transcribe_invalid_path(self):
        invalid_path = Path("nonexistent/path/audio.wav")
        self.dummy_test.transcribe(invalid_path)

    @mock.patch('src.differs.jiwer_differ')
    @mock.patch('jiwer.compute_measures', side_effect=lambda x, y: {'wer': 0.1, 'mer': 0.2})
    @mock.patch('rapidfuzz.distance.Levenshtein.editops', side_effect=lambda x, y: [])
    def test_compare(self, mock_editops, mock_compute_measures, mock_differ):
        model_transcript = "Model Transcript"
        target_transcript = "Target Transcript"
        result = self.dummy_test.compare(model_transcript, target_transcript)

        self.assertEqual(result, {'wer': 0.1, 'mer': 0.2})
        mock_editops.assert_not_called()
        mock_compute_measures.assert_called_once()

    @mock.patch('src.differs.jiwer_differ')
    @mock.patch('jiwer.compute_measures', side_effect=NotImplementedError)
    @mock.patch('rapidfuzz.distance.Levenshtein.editops', side_effect=NotImplementedError)
    def test_compare_invalid_paths(self, mock_editops, mock_compute_measures, mock_differ):
        model_transcript = "Model Transcript"
        invalid_target_transcript = "Invalid Target Transcript"

        with self.assertRaises(Exception):
            self.dummy_test.compare(model_transcript, invalid_target_transcript)

if __name__ == '__main__':
    unittest.main()
