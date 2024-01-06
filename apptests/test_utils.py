import unittest
from src.normalizers import title_normalizer
from src.differs import jiwer_differ


class TestTitleNormalizer(unittest.TestCase):

    def test_normalization_with_unicode_allowed(self):
        result = title_normalizer("Thérè ís sôme Ünicode", allow_unicode=True)
        self.assertEqual(result, "thérè-ís-sôme-ünicode")

    def test_normalization_without_unicode(self):
        result = title_normalizer("Thérè ís sôme Ünicode", allow_unicode=False)
        self.assertEqual(result, "there-is-some-unicode")

    def test_removing_special_characters(self):
        result = title_normalizer("This! is @a #sample 123_title")
        self.assertEqual(result, "this-is-a-sample-123_title")

    def test_whitespace_and_hyphen_handling(self):
        result = title_normalizer("  Some  extra   spaces and - hyphens -  ")
        self.assertEqual(result, "some-extra-spaces-and-hyphens")

    def test_empty_string_input(self):
        result = title_normalizer("")
        self.assertEqual(result, "")

    def test_numeric_input(self):
        result = title_normalizer(12345)
        self.assertEqual(result, "12345")

    def test_mixed_input(self):
        result = title_normalizer("Mixed input with 123 numbers!")
        self.assertEqual(result, "mixed-input-with-123-numbers")

    def test_none_as_input(self):
        result = title_normalizer(None)
        self.assertEqual(result, None)

class TestJiwerDiffer(unittest.TestCase):
    def test_with_detail(self):
        model_transcript = "This is a sample transcript."
        yt_transcript = "This is a sample transcription."

        result = jiwer_differ(model_transcript, yt_transcript)

        self.assertIsInstance(result, dict)
        self.assertIn("wer", result)
        self.assertIn("mer", result)
        self.assertIn("wil", result)
        self.assertIn("ins", result)
        self.assertIn("del", result)
        self.assertIn("sub", result)

        self.assertAlmostEqual(result["wer"], 0.2, places=2) 
        self.assertAlmostEqual(result["mer"], 0.25, places=2)
        self.assertAlmostEqual(result["wil"], 0.17, places=2)

    def test_match(self):
        model_transcript_perfect = "This is a sample transcript."
        yt_transcript_perfect = "This is a sample transcript."

        result_perfect = jiwer_differ(model_transcript_perfect, yt_transcript_perfect)
        self.assertIsInstance(result_perfect, dict)
        self.assertEqual(result_perfect["wer"], 0.0)  

    def test_difference(self):
        model_transcript_diff = "This is a different transcript."
        yt_transcript_diff = "Another transcript entirely."

        result_diff = jiwer_differ(model_transcript_diff, yt_transcript_diff)
        self.assertIsInstance(result_diff, dict)
        self.assertNotEqual(result_diff["wer"], 0.0)

    def test_empty_transcripts(self):
        model_transcript_empty = ""
        yt_transcript_empty = ""

        self.assertRaises(
            ValueError, jiwer_differ(model_transcript_empty, yt_transcript_empty)
        )

    def test_none_transcipt(self):
        model_transcript_empty = None
        yt_transcript_empty = ""

        self.assertRaises(
            TypeError, jiwer_differ(model_transcript_empty, yt_transcript_empty)
        )


if __name__ == '__main__':
    unittest.main()


