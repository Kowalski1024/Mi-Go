from testrunners.youtube_runner import YouTubeTestRunner


class Test_YoutubeTestRunner_run(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = YouTubeTestRunner("testplan.json", "audio", iterations=1)
        return super().setUp()

    def test_returned_type(self):
        pass

    def test_empty_list(self):
        pass

    def test_invalid_ids(self):
        pass

    def test_valid_ids(self):
        pass

    def test_valid_ids_response_keys(self):
       pass