import json
import os
import unittest
from copy import deepcopy
from os import environ, listdir, remove
from unittest.mock import MagicMock, Mock, patch, mock_open
from src.differs import jiwer_differ

from generators.youtube_generator import generate
import models
from models.dummy_test import DummyTest
from youtube_runner import YouTubeTestRunner


class Test_YoutubeTestRunner_run(unittest.TestCase):
    def setUp(self) -> None:
        self.tester = Mock()
        self.runner = YouTubeTestRunner(
            "Travel&Events_en_CAUQAQ_20231126-201522.json", "audio", "./output", iterations=1, tester=self.tester
        )
        return super().setUp()

    def test_initialization(self):
        self.assertIsNotNone(self.runner.tester.transcriber)
        self.assertIsNotNone(self.runner.tester.normalizer)
        self.assertIsNotNone(self.runner.tester.differ)
        self.assertTrue("GoogleAPI" in environ)


    @patch("models.dummy_test.DummyTest")
    @patch("generators.youtube_generator.generate")
    @patch("src.dataclasses.youtube_video.YouTubeVideo.from_dict")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_run(self, mock_dummy_test, mock_generate, mock_from_dict, mock_open, mock_json_load):
        mock_dummy_test_instance = Mock(spec=models.DummyTest)
        mock_dummy_test_instance.transcriber = lambda x: "This is a model for tests :)"
        mock_dummy_test_instance.normalizer = lambda x: x.lower()
        mock_dummy_test_instance.differ = jiwer_differ
        mock_dummy_test_instance.language = "en"
        runner = YouTubeTestRunner(
            tester=mock_dummy_test_instance,
            testplan_path="mock_testplan_path",
            audio_dir="mock_audio_dir",
            output_dir="mock_output_dir",
            iterations=2,
            save_transcripts=True,
            save_to_database=True,
            keep_audio=False
        )
        mock_video = mock_from_dict.return_value
        mock_video.youtube_transcript.return_value = "Mock Target Transcript"

        mock_video.download_mp3.return_value = "./apptests/data/sample.mp3"

        mock_dummy_test.return_value = mock_dummy_test_instance
        mock_dummy_test_instance.compare.return_value = {"result": "Mock Compare Result"}

        read_data = '{"args": {"q": "test"}, "items": [{"videoId": "123"}], "nextPageToken": "token"}'

        mock_open_func = mock_open(read_data=read_data)
        mock_open_func.return_value.__enter__.return_value.read.return_value = read_data

        with patch("builtins.open", mock_open_func), patch("json.load") as mock_json_load:
            mock_json_load.return_value = {"args": {"q": "test"}, "items": [{"videoId": "123"}], "nextPageToken": "token", "language": "en", "targetTranscript": "Mock Target Transcript"}

            runner.run()

        mock_open.assert_called_once_with("mock_testplan_path", encoding="utf8")
        mock_generate.assert_called_once_with({"pageToken": "token"})
        mock_from_dict.assert_called_once_with({"videoId": "123"})
        mock_video.youtube_transcript.assert_called_once_with(mock_transcript_test.language)
        mock_video.download_mp3.assert_called_once_with("mock_audio_dir")
        mock_dummy_test.return_value.compare.assert_called_once_with("Mock Transcribe Result", "Mock Target Transcript")
        mock_dummy_test.return_value.additional_info.assert_called_once()

    @patch("src.dataclasses.youtube_video.YouTubeVideo.from_dict")
    @patch("builtins.open")
    def test_run_with_exceptions(self, mock_from_dict, mock_open):
        mock_file = Mock()
        mock_video = Mock()
        mock_open.return_value = mock_file

        mock_from_dict.return_value = mock_video

        self.runner.tester.transcriber = None
        self.runner.tester.normalizer = None
        self.runner._iterations = 2

        self.runner._testplan_path = "mock_testplan_path"

        with patch("builtins.open"), \
            patch("src.dataclasses.youtube_video.YouTubeVideo.from_dict"), \
            patch("youtube_runner.YouTubeTestRunner.save_results"), \
            patch("generators.youtube_generator.generate"):
            with self.assertRaises(ValueError) as context:
                self.runner.run()

        self.assertEqual(str(context.exception), "Transcriber is None")


details_result = [
    {
        "channelId": "UCWlvkaA27BCrcYG6gA0K8UA",
        "channelTitle": "SMS Frankfurt Group Travel",
        "defaultAudioLanguage": "en",
        "duration": "PT14M41S",
        "generatedTranscripts": ["en"],
        "manuallyCreatedTranscripts": ["en", "de"],
        "publishTime": "2016-12-21T11:09:18Z",
        "title": "We create your Bucket List Trips and Events | Discover the Baltics with SMS Frankfurt Group Travel",
        "videoId": "YazZwd48ws0",
    }
]

search_request = {
    "args": {
        "maxResults": 10,
        "pageToken": None,
        "q": "Travel & Events",
        "regionCode": "US",
        "relevanceLanguage": "en",
        "topicId": None,
        "videoCategoryId": "19",
        "videoDuration": "medium",
        "videoLicense": "creativeCommon",
    }
}

testplan = deepcopy(search_request)
testplan["items"] = [
    {
        "channelId": "UCWlvkaA27BCrcYG6gA0K8UA",
        "channelTitle": "SMS Frankfurt Group Travel",
        "defaultAudioLanguage": "en",
        "duration": "PT14M41S",
        "manuallyCreatedTranscripts": ["en"],
        "publishTime": "2016-12-21T11:09:18Z",
        "title": "We create your Bucket List Trips and Events | Discover the Baltics with SMS Frankfurt Group Travel",
        "videoId": "YazZwd48ws0",
    },
    {
        "channelId": "UCmqdOJinYxakne7lyAXY5zw",
        "channelTitle": "Passport Kings Travel",
        "defaultAudioLanguage": "en",
        "duration": "PT6M30S",
        "generatedTranscripts": [],
        "manuallyCreatedTranscripts": ["en"],
        "publishTime": "2015-04-08T02:34:15Z",
        "title": "Men Just Traveling Abroad for Prostitutes? Passport Kings Travel Video",
        "videoId": "gI8VlFK5Jp4",
    },
    {
        "channelId": "UCkeTA80xeSa9POCGRpWTIfQ",
        "channelTitle": "travelingisrael.com",
        "defaultAudioLanguage": "en",
        "duration": "PT16M18S",
        "manuallyCreatedTranscripts": ["en"],
        "publishTime": "2023-10-18T12:38:57Z",
        "title": "Why are there so many Palestinian casualties? (The Israeli perspective) sub: DE, ES, FR, IT",
        "videoId": "OF95GenB1JI",
    },
]


class Test_YoutubeTestRunner_save_results(unittest.TestCase):
    def setUp(self) -> None:
        self.testrunner = YouTubeTestRunner("", "audio","./output", iterations=1, tester=Mock())
        return super().setUp()

    # it didnt work - TypeError is raised when value is get from dict
    def test_none_dict(self):
        self.assertRaises(TypeError, self.testrunner.save_results(None))

        json_files = [file for file in listdir("apptests") if file.endswith(".json")]
        self.assertEqual(len(json_files), 2)

    # it didnt work - KeyError is raised when value is get from dict
    def test_empty_dict(self):
        self.assertRaises(KeyError, self.testrunner.save_results({}))
        
        json_files = [file for file in listdir("apptests") if file.endswith(".json")]
        self.assertEqual(len(json_files), 2)

    def test_valid_dict(self):
        path = "simpleTest.json"
        runner = YouTubeTestRunner(path, "audio", "", iterations=1, tester=Mock())
        generated_testplan = generate(search_request.get("args"))
        runner.save_results(generated_testplan)

        json_files = [file for file in listdir() if file.endswith(".json")]
        self.assertEqual(len(json_files), 1)

        for json_file in json_files:
            remove(json_file)


        
