import unittest

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.youtube import (
    YouTubeBase,
    YouTubeResult,
    YouTubeTestPlan,
    YouTubeVideo,
)


class TestYouTubeModels(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        YouTubeBase.metadata.create_all(engine)
        self.session = Session(engine)

    def tearDown(self):
        self.session.close()

    def test_youtube_testplan(self):
        testplan_data = {
            "args": {
                "maxResults": 10,
                "pageToken": "token",
                "q": "test",
                "regionCode": "US",
                "relevanceLanguage": "en",
                "topicId": "topic",
                "videoCategoryId": "category",
                "videoDuration": "medium",
                "videoLicense": "creativeCommon",
            },
            "items": [{"videoId": "123"}],
            "nextPageToken": "token",
            "etag": "abc123",
        }

        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        result = (
            self.session.query(YouTubeTestPlan)
            .filter_by(testplan_name="test_plan")
            .first()
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.max_results, 10)
        self.assertEqual(result.page_token, "token")
        self.assertEqual(result.q, "test")
        self.assertEqual(result.total_results, 1)
        self.assertEqual(result.success, 0)  # No "results" in testplan_data["items"]
        self.assertEqual(result.etag, "abc123")

    def test_youtube_video(self):
        video_data = {
            "videoId": "123",
            "title": "Test Video",
            "channelId": "channel123",
            "channelTitle": "Test Channel",
            "defaultAudioLanguage": "en",
            "duration": "PT10M",
            "publishTime": "2022-01-01T00:00:00Z",
        }

        youtube_video = YouTubeVideo.from_video(video_data)
        self.session.add(youtube_video)
        self.session.commit()

        result = self.session.query(YouTubeVideo).filter_by(video_id="123").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Test Video")
        self.assertEqual(result.channel_id, "channel123")
        self.assertEqual(result.default_audio_language, "en")
        self.assertEqual(result.duration, "PT10M")
        self.assertEqual(result.publish_time, "2022-01-01T00:00:00Z")

    def test_youtube_result(self):
        testplan_data = {
            "args": {
                "maxResults": 10,
                "pageToken": "token",
                "q": "test",
                "regionCode": "US",
                "relevanceLanguage": "en",
                "topicId": "topic",
                "videoCategoryId": "category",
                "videoDuration": "medium",
                "videoLicense": "creativeCommon",
            },
            "items": [{"videoId": "123"}],
            "nextPageToken": "token",
            "etag": "abc123",
        }

        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        video_data = {
            "videoId": "123",
            "title": "Test Video",
            "channelId": "channel123",
            "channelTitle": "Test Channel",
            "defaultAudioLanguage": "en",
            "duration": "PT10M",
            "publishTime": "2022-01-01T00:00:00Z",
        }

        youtube_video = YouTubeVideo.from_video(video_data)
        self.session.add(youtube_video)
        self.session.commit()

        result_data = {
            "modelName": "TestModel",
            "language": "en",
            "wer": 0.5,
            "mer": 0.2,
            "wil": 0.3,
            "wip": 0.4,
            "hits": 100,
            "substitutions": 10,
            "deletions": 5,
            "insertions": 5,
            "modelSettings": "{'param': 'value'}",
        }

        youtube_result = YouTubeResult.from_result(
            youtube_testplan.id, youtube_video.video_id, result_data
        )
        self.session.add(youtube_result)
        self.session.commit()

        result = self.session.query(YouTubeResult).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.model_name, "TestModel")
        self.assertEqual(result.language, "en")
        self.assertEqual(result.wer, 0.5)
        self.assertEqual(result.mer, 0.2)
        self.assertEqual(result.wil, 0.3)
        self.assertEqual(result.wip, 0.4)
        self.assertEqual(result.hits, 100)
        self.assertEqual(result.substitutions, 10)
        self.assertEqual(result.deletions, 5)
        self.assertEqual(result.insertions, 5)
        self.assertEqual(result.model_settings, "{'param': 'value'}")

    def test_youtube_testplan_no_success(self):
        testplan_data = {
            "args": {
                "maxResults": 10,
                "pageToken": "token",
                "q": "test",
                "regionCode": "US",
                "relevanceLanguage": "en",
                "topicId": "topic",
                "videoCategoryId": "category",
                "videoDuration": "medium",
                "videoLicense": "creativeCommon",
            },
            "items": [{"videoId": "123"}],
            "nextPageToken": "token",
            "etag": "abc123",
        }

        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        result = (
            self.session.query(YouTubeTestPlan)
            .filter_by(testplan_name="test_plan")
            .first()
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.success, 0)  # No "results" in testplan_data["items"]

    def test_youtube_testplan_with_success(self):
        testplan_data = {
            "args": {
                "maxResults": 10,
                "pageToken": "token",
                "q": "test",
                "regionCode": "US",
                "relevanceLanguage": "en",
                "topicId": "topic",
                "videoCategoryId": "category",
                "videoDuration": "medium",
                "videoLicense": "creativeCommon",
            },
            "items": [{"videoId": "123", "results": {"wer": 0.1}}],
            "nextPageToken": "token",
            "etag": "abc123",
        }

        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        result = (
            self.session.query(YouTubeTestPlan)
            .filter_by(testplan_name="test_plan")
            .first()
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.success, 1)

    def test_youtube_result_no_model_settings(self):
        testplan_data = {
            "args": {
                "maxResults": 10,
                "pageToken": "token",
                "q": "test",
                "regionCode": "US",
                "relevanceLanguage": "en",
                "topicId": "topic",
                "videoCategoryId": "category",
                "videoDuration": "medium",
                "videoLicense": "creativeCommon",
            },
            "items": [{"videoId": "123"}],
            "nextPageToken": "token",
            "etag": "abc123",
        }

        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        video_data = {
            "videoId": "123",
            "title": "Test Video",
            "channelId": "channel123",
            "channelTitle": "Test Channel",
            "defaultAudioLanguage": "en",
            "duration": "PT10M",
            "publishTime": "2022-01-01T00:00:00Z",
        }

        youtube_video = YouTubeVideo.from_video(video_data)
        self.session.add(youtube_video)
        self.session.commit()

        result_data = {
            "modelName": "TestModel",
            "language": "en",
            "wer": 0.5,
            "mer": 0.2,
            "wil": 0.3,
            "wip": 0.4,
            "hits": 100,
            "substitutions": 10,
            "deletions": 5,
            "insertions": 5,
        }

        youtube_result = YouTubeResult.from_result(
            youtube_testplan.id, youtube_video.video_id, result_data
        )
        self.session.add(youtube_result)
        self.session.commit()

        result = self.session.query(YouTubeResult).first()
        self.assertIsNotNone(result)
        self.assertIsNone(result.model_settings)

    def test_youtube_result_with_model_settings(self):
        testplan_data = {
            "args": {
                "maxResults": 10,
                "pageToken": "token",
                "q": "test",
                "regionCode": "US",
                "relevanceLanguage": "en",
                "topicId": "topic",
                "videoCategoryId": "category",
                "videoDuration": "medium",
                "videoLicense": "creativeCommon",
            },
            "items": [{"videoId": "123"}],
            "nextPageToken": "token",
            "etag": "abc123",
        }

        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        video_data = {
            "videoId": "123",
            "title": "Test Video",
            "channelId": "channel123",
            "channelTitle": "Test Channel",
            "defaultAudioLanguage": "en",
            "duration": "PT10M",
            "publishTime": "2022-01-01T00:00:00Z",
        }

        youtube_video = YouTubeVideo.from_video(video_data)
        self.session.add(youtube_video)
        self.session.commit()

        result_data = {
            "modelName": "TestModel",
            "language": "en",
            "wer": 0.5,
            "mer": 0.2,
            "wil": 0.3,
            "wip": 0.4,
            "hits": 100,
            "substitutions": 10,
            "deletions": 5,
            "insertions": 5,
            "modelSettings": "{'param': 'value'}",
        }

        youtube_result = YouTubeResult.from_result(
            youtube_testplan.id, youtube_video.video_id, result_data
        )
        self.session.add(youtube_result)
        self.session.commit()

        result = self.session.query(YouTubeResult).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.model_settings, "{'param': 'value'}")
