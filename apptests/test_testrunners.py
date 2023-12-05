import unittest
from copy import deepcopy
from os import environ, listdir

from generators.youtube_generator import generate
from testrunners.youtube_runner import YouTubeTestRunner


class Test_YoutubeTestRunner_run(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = YouTubeTestRunner(
            "Travel&Events_en_CAUQAQ_20231126-201522.json", "audio", iterations=1
        )
        return super().setUp()

    def test_initialization(self):
        self.assertIsNotNone(self.runner.transciber)
        self.assertIsNotNone(self.runner.normalizer)
        self.assertIsNotNone(self.runner.differ)
        self.assertTrue("GoogleAPI" in environ)

    def test_empty_list(self):
        pass

    def test_invalid_ids(self):
        pass

    def test_valid_ids(self):
        pass

    def test_valid_ids_response_keys(self):
        pass


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


class Test_YoutubeTestRunner_video_details(unittest.TestCase):
    def setUp(self) -> None:
        self.testrunner = YouTubeTestRunner("", "audio", iterations=1)
        return super().setUp()

    def test_none_dict(self):
        self.assertEqual(self.testrunner.video_details(None), [])

    def test_empty_dict(self):
        self.assertEqual(self.testrunner.video_details({}), [])

    def test_valid_dict(self):
        runner = YouTubeTestRunner("simpleTest.json", "audio", iterations=1)
        generated_testplan = generate(search_request.get("args"))
        self.assertEqual(runner.video_details(generated_testplan), details_result)


class Test_YoutubeTestRunner_save_results(unittest.TestCase):
    def setUp(self) -> None:
        self.testrunner = YouTubeTestRunner("", "audio", iterations=1)
        return super().setUp()

    def test_none_dict(self):
        self.testrunner.save_results(None)

        json_files = [file for file in listdir("apptests") if file.endswith(".json")]
        self.assertEqual(len(json_files), 2)

    def test_empty_dict(self):
        self.testrunner.save_results({})

        json_files = [file for file in listdir("apptests") if file.endswith(".json")]
        self.assertEqual(len(json_files), 2)

    def test_valid_dict(self):
        runner = YouTubeTestRunner("simpleTest.json", "audio", iterations=1)
        generated_testplan = generate(search_request.get("args"))
        runner.save_results(generated_testplan)

        json_files = [file for file in listdir("apptests") if file.endswith(".json")]
        self.assertEqual(len(json_files), 3)
