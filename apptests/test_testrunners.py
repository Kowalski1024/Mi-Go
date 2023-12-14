import unittest
from copy import deepcopy
from os import environ, listdir
from unittest.mock import Mock, patch

from generators.youtube_generator import generate
from models.dummy_test import DummyTest
from youtube_runner import YouTubeTestRunner


class Test_YoutubeTestRunner_run(unittest.TestCase):
    def setUp(self) -> None:
        self.tester = Mock()
        self.runner = YouTubeTestRunner(
            DummyTest(), "Travel&Events_en_CAUQAQ_20231126-201522.json", "audio", iterations=1, 
        )
        return super().setUp()

    def test_initialization(self):
        self.assertIsNotNone(self.runner.tester.transcriber)
        self.assertIsNotNone(self.runner.tester.normalizer)
        self.assertIsNotNone(self.runner.tester.differ)
        self.assertTrue("GoogleAPI" in environ)

    @patch("builtins.open", new_callable=Mock, create=True)
    @patch("src.dataclasses.youtube_video.YouTubeVideo.from_dict", return_value=Mock())
    @patch("youtube_runner.YouTubeTestRunner.save_results", return_value=None)
    @patch("generators.youtube_generator.generate", return_value=None)
    def test_success_run(
        self, mock_generate, mock_save_results, mock_from_dict, mock_open
    ):
        mock_file = mock_open.return_value
        mock_video = mock_from_dict.return_value
        mock_audio = Mock()
        mock_transcribe_result = "Mock Transcribe Result"
        mock_compare_result = {"result": "Mock Compare Result"}

        self.tester.transcriber = Mock()
        self.tester.transcriber.transcribe.return_value = mock_transcribe_result
        mock_video.youtube_transcript.return_value = "Mock Target Transcript"
        mock_video.download_mp3.return_value = mock_audio
        self.tester.compare.return_value = mock_compare_result
        self.tester.additional_info.return_value = {"additional_info": "Mock Additional Info"}

        testplan_data = {
            "args": {"pageToken": "mock_page_token"},
            "items": [{"videoId": "mock_video_id"}],
            "nextPageToken": "mock_next_page_token"
        }
        self.runner._testplan_path = "mock_testplan_path"
        self.runner._iterations = 1

        with patch("builtins.open", mock_open), \
             patch("src.dataclasses.youtube_video.YouTubeVideo.from_dict", mock_from_dict), \
             patch("youtube_runner.YouTubeTestRunner.save_results", mock_save_results), \
             patch("generators.youtube_generator.generate", mock_generate):
            self.runner.run()

        mock_open.assert_called_once_with("mock_testplan_path", encoding="utf8")
        mock_from_dict.assert_called_once_with({"videoId": "mock_video_id"})
        mock_video.youtube_transcript.assert_called_once_with(self.tester.language)
        mock_video.download_mp3.assert_called_once_with(self.runner._audio_dir)
        self.tester.transcriber.transcribe.assert_called_once_with(mock_audio)
        self.tester.compare.assert_called_once_with(
            mock_transcribe_result, "Mock Target Transcript"
        )
        self.tester.additional_info.assert_called_once()

        mock_save_results.assert_called_once_with(testplan_data)
        mock_generate.assert_called_once_with({"pageToken": "mock_next_page_token"})

    @patch("builtins.open")
    @patch("src.dataclasses.youtube_video.YouTubeVideo.from_dict")
    @patch("youtube_runner.YouTubeTestRunner.save_results")
    @patch("generators.youtube_generator.generate")
    def test_run_with_exceptions(self, mock_generate, mock_save_results, mock_from_dict, mock_open):
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
        self.testrunner = YouTubeTestRunner(DummyTest(), "", "audio", iterations=1)
        return super().setUp()

    def test_none_dict(self):
        self.assertRaises(KeyError, self.testrunner.save_results(None))

        json_files = [file for file in listdir("apptests") if file.endswith(".json")]
        self.assertEqual(len(json_files), 2)

    def test_empty_dict(self):
        self.assertRaises(KeyError, self.testrunner.save_results({}))
        
        json_files = [file for file in listdir("apptests") if file.endswith(".json")]
        self.assertEqual(len(json_files), 2)

    def test_valid_dict(self):
        runner = YouTubeTestRunner(DummyTest(), "simpleTest.json", "audio", iterations=1)
        generated_testplan = generate(search_request.get("args"))
        runner.save_results(generated_testplan)

        json_files = [file for file in listdir() if file.endswith(".json")]
        self.assertEqual(len(json_files), 3)
