import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

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


results_example = {
    "args": {
        "maxResults": 10,
        "q": "Travel & Events",
        "regionCode": "US",
        "relevanceLanguage": "en",
        "videoCategoryId": "19",
        "videoDuration": "medium",
        "videoLicense": "creativeCommon",
        "pageToken": "CAEQAA",
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
    def test_returned_type(self):
        self.assertIsInstance(gen.categories_request("en_US", "GB"), dict)

    def test_invalid_params(self):
        self.assertRaises(KeyError, gen.categories_request("invalid", "invalid"))

    def test_empty_params(self):
        self.assertRaises(KeyError, gen.categories_request(None, None))

    def test_valid_params(self):
        response = gen.categories_request("en_US", "GB")
        self.assertIsNotNone(response.get("items"))


class Test_assignable_categories(unittest.TestCase):
    def test_valid_params(self):
        response = gen.assignable_categories("en_US", "GB")
        self.assertTrue(len(response["items"]) > 0)
        self.assertIsInstance(response, dict)

    def test_invalid_params(self):
        self.assertRaises(KeyError, gen.assignable_categories("x", ""))


class Test_search_request(unittest.TestCase):
    def test_empty_dict_params(self):
        self.assertRaises(KeyError, gen.search_request(args={}))

    def test_empty_params(self):
        self.assertRaises(KeyError, gen.search_request(args=None))

    def test_valid_params(self):
        response = gen.search_request(args=search_request.get("args"))
        self.assertIsInstance(response, dict)
        self.assertTrue(len(response["items"]) > 0)
        self.assertTrue("videoCategoryId" in response.keys())
        self.assertEqual(
            response.get("videoCategoryId"),
            search_request.get("args").get("videoCategoryId"),
        )


# class Test_results_parser(unittest.TestCase):
# def test_valid_params(self):
#     response = gen.results_parser()
#     self.assertIsNotNone(response.get(1))


if __name__ == "__main__":
    unittest.main()
