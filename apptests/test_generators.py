import unittest
from copy import deepcopy
from pathlib import Path
import json
from unittest.mock import mock_open, patch

import generators.youtube_generator as gen

empty_response_details = {
    "etag": "YIUPVpqNjppyCWOZfL-19bLb7uk",
    "items": [],
    "kind": "youtube#videoListResponse",
    "pageInfo": {"resultsPerPage": 0, "totalResults": 0},
}
example_response = {
    "kind": "youtube#searchListResponse",
    "etag": "wPpqdJzsY8IQM6ZYDqXcwWLEiVM",
    "nextPageToken": "CAEQAA",
    "regionCode": "US",
    "pageInfo": {"totalResults": 273, "resultsPerPage": 1},
    "items": [
        {
            "kind": "youtube#searchResult",
            "etag": "NBmdLBv-G2RxAuLNA7IPe_s4x7Q",
            "id": {"kind": "youtube#video", "videoId": "YazZwd48ws0"},
            "snippet": {
                "publishedAt": "2016-12-21T11:09:18Z",
                "channelId": "UCWlvkaA27BCrcYG6gA0K8UA",
                "title": "We create your Bucket List Trips and Events | Discover the Baltics with SMS Frankfurt Group Travel",
                "description": "Tailormade Event and Incentives | Discover the Baltics with SMS Frankfurt Group Travel - We create your Bucket List Trips and ...",
                "thumbnails": {
                    "default": {
                        "url": "https://i.ytimg.com/vi/YazZwd48ws0/default.jpg",
                        "width": 120,
                        "height": 90,
                    }
                },
                "channelTitle": "SMS Frankfurt Group Travel",
                "publishTime": "2016-12-21T11:09:18Z",
            },
        }
    ],
}
parsed_example = [
    {
        "videoId": "YazZwd48ws0",
        "channelId": "UCWlvkaA27BCrcYG6gA0K8UA",
        "title": "We create your Bucket List Trips and Events | Discover the Baltics with SMS Frankfurt Group Travel",
        "channelTitle": "SMS Frankfurt Group Travel",
        "publishTime": "2016-12-21T11:09:18Z",
    }
]


search_request = {
    "args": {'maxResults': 10,
 'pageToken': None,
 'q': 'Travel & Events',
 'regionCode': 'US',
 'relevanceLanguage': 'en',
 'topicId': None,
 'videoCategoryId': '19',
 'videoDuration': 'medium',
 'videoLicense': 'creativeCommon'}
}


results_example = {
    "args": {
        "maxResults": 10,
        "q": "Travel & Events",
        "regionCode": "US",
        "relevanceLanguage": "en",
        "videoCategoryId": "19",
        "videoDuration": "medium",
        "videoLicense": "creativeCommon",
        "pageToken": "CAEQAA"
    }
}

class Test_videos_details_request(unittest.TestCase):
    def setUp(self) -> None:
        self.expected_keys = ["kind", "etag", "items", "pageInfo"]
        self.valid_ids = ["gI8VlFK5Jp4", "YazZwd48ws0"]
        return super().setUp()

    def test_returned_type(self):
        self.assertIsInstance(gen.videos_details_request([]), dict)

    def test_empty_list(self):
        self.assertEqual(gen.videos_details_request([]), empty_response_details)

    def test_invalid_ids(self):
        self.assertEqual(
            gen.videos_details_request(["invalid_id"]), empty_response_details
        )

    def test_valid_ids(self):
        self.assertNotEqual(
            gen.videos_details_request(self.valid_ids),
            empty_response_details,
        )

    def test_valid_ids_response_keys(self):
        response = gen.videos_details_request(self.valid_ids)

        for key in self.expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, response)


class Test_categories_request(unittest.TestCase):
    # should return info about 400 response?
    # def test_returned_type(self):
    #     self.assertIsInstance(gen.categories_request("", ""), dict)

    # def test_invalid_params(self):
    #     self.assertIsNotNone(gen.categories_request("invalid", "invalid").get("error"))

    # def test_empty_params(self):
    #     self.assertIsNotNone(gen.categories_request(None, None).get("error"))

    def test_valid_params(self):
        response = gen.categories_request("en_US", "GB")
        self.assertIsNone(response.get("error"))
        self.assertIsNotNone(response.get("items"))


class Test_assignable_categories(unittest.TestCase):
    def test_valid_params(self):
        response = gen.assignable_categories("en_US", "GB")
        self.assertIsNotNone(response.get(1))

    # same as above
    # def test_invalid_params(self):
    #     response = gen.assignable_categories("x", "")
    #     self.assertIsNone(response.get(1))
    #     self.assertNone(response.get("error"))


class Test_search_request(unittest.TestCase):
    # def test_empty_dict_params(self):
    #     response = gen.search_request(args={})
    #     self.assertNotNil(response.get("error"))

    # def test_empty_params(self):
    #     response = gen.search_request(args=None)
    #     self.assertIsNotNone(response)

    def test_valid_params(self):
        response = gen.search_request(args=search_request.get("args"))
        self.assertIsNotNone(response)


class Test_results_parser(unittest.TestCase):
    def setUp(self) -> None:
        self.expected_keys = [
            "videoId",
            "channelId",
            "channelTitle",
            "publishTime",
            "title",
        ]
        return super().setUp()

    def test_valid_params(self):
        response = gen.results_parser(example_response)
        self.assertIsNotNone(response.get("items"))

        self.assertIsNone(response.get("kind"))
        self.assertIsNone(response.get("pageInfo"))
        for key in self.expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, response.get("items")[0])
                self.assertIsNotNone(response.get("items")[0].get(key))

    # it should check if results have items key
    # def test_empty_results_param(self):
    #     self.assertRaises(KeyError, gen.results_parser({}))


class Test_add_video_details(unittest.TestCase):
    def setUp(self) -> None:
        self.ok_parsed_example = deepcopy(parsed_example)
        self.nok_parsed_example = deepcopy(parsed_example)
        return super().setUp()

    def test_valid_video_list(self):
        gen.add_video_details(self.ok_parsed_example)
        video = self.ok_parsed_example[0]
        self.assertIsNotNone(video.get("duration"))
        self.assertIsNotNone(video.get("defaultAudioLanguage"))

    # it should check if videoId key exists
    # def test_invalid_video_list(self):
    #     self.nok_parsed_example[0].pop("videoId")
    #     gen.add_video_details(self.nok_parsed_example)
    #     video = self.nok_parsed_example[0]
    #     self.assertIsNone(video.get("duration"))
    #     self.assertIsNone(video.get("defaultAudioLanguage"))


class Test_add_transcripts_info(unittest.TestCase):
    def setUp(self) -> None:
        self.ok_parsed_example = deepcopy(parsed_example)
        self.nok1_parsed_example = deepcopy(parsed_example)
        self.nok2_parsed_example = deepcopy(parsed_example)
        return super().setUp()

    def test_valid_video_list(self):
        gen.add_transcripts_info(self.ok_parsed_example)
        video = self.ok_parsed_example[0]
        self.assertIsNotNone(video.get("manuallyCreatedTranscripts"))
        self.assertIsNotNone(video.get("generatedTranscripts"))

    def test_invalid_video_list(self):
        self.nok2_parsed_example[0].pop("title")
        gen.add_transcripts_info(self.nok2_parsed_example)
        video = self.nok2_parsed_example[0]
        self.assertIsNotNone(video.get("manuallyCreatedTranscripts"))
        self.assertIsNotNone(video.get("generatedTranscripts"))

    # it should check if videoId key exists
    # def test_lack_of_videoid(self):
    #     self.nok1_parsed_example[0].pop("videoId")
    #     gen.add_transcripts_info(self.nok1_parsed_example)
    #     video = self.nok1_parsed_example[0]
    #     self.assertIsNone(video.get("manuallyCreatedTranscripts"))
    #     self.assertIsNone(video.get("generatedTranscripts"))

class Test_save_as_json(unittest.TestCase):

    @patch('generators.youtube_generator.time') 
    @patch('builtins.open', new_callable=mock_open)
    def test_valid_data(self, mock_open, mock_time):
        category = "Test Category"

        mock_time.strftime.return_value = "20231126-000000"
        mock_open.return_value.write.return_value = len(results_example)

        with patch('pathlib.Path.mkdir') as mock_mkdir:
            gen.save_as_json(results_example, "/path/to/destination", category)

        expected_filename = "TestCategory_en_CAEQAA_20231126-000000.json"
        expected_filepath = Path("/path/to/destination/" + expected_filename)

        mock_mkdir.assert_called_once_with(exist_ok=True)

        mock_open.assert_called_once_with(expected_filepath, "w", encoding="utf-8")

        write_call_args = mock_open.return_value.__enter__().write.call_args_list
        written_content = ""
        for call_args, _ in write_call_args:
            written_content += call_args[0]
        expected_content = json.dumps(results_example, ensure_ascii=False, indent=4, sort_keys=True)
        self.assertEqual(written_content, expected_content)

    #it should return user friendly error (not return AtrributeError and stop program)
    # @patch('generators.youtube_generator.time') 
    # @patch('builtins.open', new_callable=mock_open)
    # def test_invalid_keys(self, mock_open, mock_time):
    #     category = "Test Category"

    #     mock_time.strftime.return_value = "20231126-000000"
    #     mock_open.return_value.write.return_value = len(results_example)

    #     with patch('pathlib.Path.mkdir'):
    #         gen.save_as_json({}, "/path/to/destination", category)


class Test_generate(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
