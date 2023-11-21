import unittest

import generators.youtube_generator as gen

empty_response_details = {
    "etag": "YIUPVpqNjppyCWOZfL-19bLb7uk",
    "items": [],
    "kind": "youtube#videoListResponse",
    "pageInfo": {"resultsPerPage": 0, "totalResults": 0},
}

search_request = {
    "args": {
        "maxResults": 10,
        "q": "Travel & Events",
        "regionCode": "US",
        "relevanceLanguage": "en",
        "videoCategoryId": "19",
        "videoDuration": "medium",
        "videoLicense": "creativeCommon",
    }
}


class Test_videos_details_request(unittest.TestCase):
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
            gen.videos_details_request(["gI8VlFK5Jp4", "YazZwd48ws0"]),
            empty_response_details,
        )

    def test_valid_ids_response_keys(self):
        expected_keys = ["kind", "etag", "items", "pageInfo"]
        response = gen.videos_details_request(["gI8VlFK5Jp4", "YazZwd48ws0"])

        for key in expected_keys:
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
    def test_valid_params(self):
        response = gen.results_parser()
        self.assertIsNotNone(response.get(1))


if __name__ == "__main__":
    unittest.main()
