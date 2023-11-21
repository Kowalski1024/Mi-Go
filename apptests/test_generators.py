import unittest

from generators.youtube_generator import videos_details_request

empty_response = {'etag': 'YIUPVpqNjppyCWOZfL-19bLb7uk', 
                      'items': [], 
                      'kind': 'youtube#videoListResponse',
                      'pageInfo': {'resultsPerPage': 0, 'totalResults': 0}
                      }


class Test_videos_details_request(unittest.TestCase):
    def test_check_returned_type(self):
        self.assertEqual(type(videos_details_request([])), dict)

    def test_check_empty_list(self):
        self.assertEqual(videos_details_request([]), empty_response)

    def test_check_invalid_ids(self):
        self.assertEqual(videos_details_request(["invalid_id"]), empty_response)

if __name__ == '__main__':
    unittest.main()