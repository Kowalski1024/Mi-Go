import json
import os
import unittest
from copy import deepcopy
from os import environ, listdir, remove
from unittest.mock import MagicMock, Mock, mock_open, patch

import models
from generators.youtube_generator import generate
from models.dummy_test import DummyTest
from src.dataclasses.youtube_video import YouTubeVideo
from src.differs import jiwer_differ
from youtube_runner import YouTubeTestRunner


class Test_YoutubeTestRunner_run(unittest.TestCase):
    def setUp(self) -> None:
        self.tester = Mock()
        self.mock_dummy_test_instance = Mock(
            spec=models.DummyTest(
                transcriber=lambda x: "This is a model for tests :)",
                normalizer=lambda x: x.lower(),
                differ=jiwer_differ,
            )
        )
        self.mock_dummy_test_instance.transcribe.return_value = (
            "This is a model for tests :)"
        )
        self.mock_dummy_test_instance.additional_info.return_value = {
            "modelName": "DummyTest",
            "language": "en",
            "modelSettings": "{'channel_selector': 'average', 'batch_size': 1}",
        }
        self.mock_dummy_test_instance.compare.return_value = {
            "result": "Mock Compare Result"
        }
        self.runner = YouTubeTestRunner(
            tester=self.mock_dummy_test_instance,
            testplan_path="./apptests/data/simpleTest.json",
            audio_dir="mock_audio_dir",
            output_dir="mock_output_dir",
            iterations=1,
            save_transcripts=True,
            save_to_database=False,
            keep_audio=True,
        )
        self.mock_video = MagicMock(spec=YouTubeVideo)
        self.mock_video.youtube_transcript.return_value = "This is a model for tests :)"
        self.mock_video.download_mp3.return_value = "./apptests/data/sample.mp3"

        self.read_data = '{"args": {"q": "test"}, "items": [{"videoId": "123"}], "nextPageToken": "token"}'
        self.json_load_data = {
            "args": {"q": "test"},
            "items": [{"videoId": "123"}],
            "nextPageToken": "token",
            "language": "en",
            "targetTranscript": "Mock Target Transcript",
        }

        return super().setUp()

    def test_initialization(self):
        self.assertIsNotNone(self.runner.tester.transcriber)
        self.assertIsNotNone(self.runner.tester.normalizer)
        self.assertIsNotNone(self.runner.tester.differ)
        self.assertTrue("GoogleAPI" in environ)

    @patch("generators.youtube_generator.generate")
    @patch("src.dataclasses.youtube_video.YouTubeVideo.from_dict")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("json.dump")
    def test_run(
        self, mock_generate, mock_from_dict, mock_open, mock_json_load, mock_json_dump
    ):
        mock_from_dict.return_value = self.mock_video

        mock_open_func = mock_open(read_data=self.read_data)
        mock_open_func.return_value.__enter__.return_value.read.return_value = (
            self.read_data
        )

        def custom_json_dump(obj, f, ensure_ascii, indent):
            serializable_obj = {}
            for key, value in obj.items():
                if isinstance(value, Mock):
                    serializable_obj[
                        key
                    ] = f"Mock object of type {value._spec_class.__name__}"
                else:
                    serializable_obj[key] = value

            json.dump(serializable_obj, f, ensure_ascii=ensure_ascii, indent=indent)

        mock_json_dump.side_effect = custom_json_dump

        with patch("builtins.open", mock_open_func), patch(
            "json.load"
        ) as mock_json_load:
            mock_json_load.return_value = self.json_load_data
            self.runner.run()
            mock_generate.assert_called_once_with(
                mock_json_load.return_value,
                mock_open_func.return_value.__enter__.return_value,
                ensure_ascii=False,
            )

        mock_open.assert_called_once_with(read_data=self.read_data)
        self.mock_dummy_test_instance.additional_info.assert_called_once()

    @patch("src.dataclasses.youtube_video.YouTubeVideo.from_dict")
    @patch("builtins.open")
    def test_run_with_exceptions(self, mock_from_dict, mock_open):
        mock_file = Mock()
        mock_open.return_value = mock_file

        mock_from_dict.return_value = self.mock_video

        self.runner.tester.transcriber = None
        self.runner.tester.normalizer = None

        with patch("builtins.open"), patch(
            "src.dataclasses.youtube_video.YouTubeVideo.from_dict"
        ), patch("youtube_runner.YouTubeTestRunner.save_results"), patch(
            "generators.youtube_generator.generate"
        ):
            with self.assertRaises(ValueError) as context:
                self.runner.run()

        self.assertEqual(str(context.exception), "Transcriber is None")


class Test_YoutubeTestRunner_save_results(unittest.TestCase):
    def setUp(self) -> None:
        self.testrunner = YouTubeTestRunner(
            "", "audio", "./output", iterations=1, tester=Mock()
        )
        return super().setUp()

    # it didnt work - KeyError is raised when value is get from dict
    def test_empty_dict(self):
        self.assertRaises(KeyError, self.testrunner.save_results({}))

        json_files = [file for file in listdir("apptests") if file.endswith(".json")]
        self.assertEqual(len(json_files), 2)

    def test_valid_dict(self):
        path = "apptests/data/simpleTest.json"
        runner = YouTubeTestRunner(path, "audio", "", iterations=1, tester=Mock())

        with open(path, "r", encoding="utf-8") as file:
            testplan_data = json.load(file)

        runner.save_results(testplan_data)

        json_files = [file for file in listdir() if file.endswith(".json")]
        self.assertEqual(len(json_files), 1)

        for json_file in json_files:
            remove(json_file)
