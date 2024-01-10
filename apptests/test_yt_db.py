import json
import unittest
from copy import deepcopy

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.youtube import (
    YouTubeBase,
    YouTubeResult,
    YouTubeTestPlan,
    YouTubeVideo,
)
from src.utils import insert_youtube_result

path = "apptests/data/"

with open(f"{path}testplan1.json", "r", encoding="utf-8") as file:
    testplan_data = json.load(file)

with open(f"{path}testplan2.json", "r", encoding="utf-8") as file:
    testplan_data2 = json.load(file)


result_data = testplan_data2["items"][0]["results"]


class TestYouTubeModels(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        YouTubeBase.metadata.create_all(engine)
        self.session = Session(engine)

    def tearDown(self):
        self.session.close()

    def test_youtube_testplan(self):
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
        self.assertEqual(result.success, 0)
        self.assertEqual(result.etag, "abc123")

    def test_youtube_video(self):
        youtube_video = YouTubeVideo.from_video(testplan_data["items"][0])
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
        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        youtube_video = YouTubeVideo.from_video(testplan_data["items"][0])
        self.session.add(youtube_video)
        self.session.commit()

        youtube_result = YouTubeResult.from_result(
            youtube_testplan.id, youtube_video.video_id, result_data
        )
        self.session.add(youtube_result)
        self.session.commit()

        result = self.session.query(YouTubeResult).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.model_name, "TestModel")
        self.assertEqual(result.language, "en")
        self.assertEqual(result.wer, 0.1)
        self.assertEqual(result.mer, 1.0)
        self.assertEqual(result.wil, 1.0)
        self.assertEqual(result.wip, 1.0)
        self.assertEqual(result.hits, 1)
        self.assertEqual(result.substitutions, 12)
        self.assertEqual(result.deletions, 12)
        self.assertEqual(result.insertions, 65)
        self.assertEqual(result.model_settings, "{'param': 'value'}")

    def test_youtube_testplan_no_success(self):
        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        result = (
            self.session.query(YouTubeTestPlan)
            .filter_by(testplan_name="test_plan")
            .first()
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.success, 0)

    def test_youtube_testplan_with_success(self):
        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data2)
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
        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        youtube_video = YouTubeVideo.from_video(testplan_data["items"][0])
        self.session.add(youtube_video)
        self.session.commit()

        result_data_copy = deepcopy(result_data).pop("modelSettings")

        youtube_result = YouTubeResult.from_result(
            youtube_testplan.id, youtube_video.video_id, result_data_copy
        )
        self.session.add(youtube_result)
        self.session.commit()

        result = self.session.query(YouTubeResult).first()
        self.assertIsNotNone(result)
        self.assertIsNone(result.model_settings)

    def test_youtube_result_with_model_settings(self):
        youtube_testplan = YouTubeTestPlan.from_testplan("test_plan", testplan_data)
        self.session.add(youtube_testplan)
        self.session.commit()

        youtube_video = YouTubeVideo.from_video(testplan_data["items"][0])
        self.session.add(youtube_video)
        self.session.commit()

        youtube_result = YouTubeResult.from_result(
            youtube_testplan.id, youtube_video.video_id, result_data
        )
        self.session.add(youtube_result)
        self.session.commit()

        result = self.session.query(YouTubeResult).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.model_settings, "{'param': 'value'}")


class TestInsertYouTubeResult(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        YouTubeTestPlan.metadata.create_all(engine)
        YouTubeVideo.metadata.create_all(engine)
        YouTubeResult.metadata.create_all(engine)
        self.session = Session(engine)

    def tearDown(self):
        self.session.close()

    def test_insert_youtube_result_success(self):
        testplan_name = "test_plan"
        success = insert_youtube_result(self.session, testplan_name, testplan_data2)
        self.assertTrue(success)

        testplan = (
            self.session.query(YouTubeTestPlan)
            .filter_by(testplan_name=testplan_name)
            .first()
        )
        self.assertIsNotNone(testplan)
        self.assertEqual(testplan.total_results, 1)

        video = self.session.query(YouTubeVideo).filter_by(video_id="123").first()
        self.assertIsNotNone(video)

        result = self.session.query(YouTubeResult).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.model_name, "TestModel")
        self.assertEqual(result.language, "en")
        self.assertEqual(result.wer, 0.1)
        self.assertEqual(result.mer, 1)
        self.assertEqual(result.wil, 1)
        self.assertEqual(result.wip, 1)

    def test_insert_youtube_result_duplicate_testplan(self):
        testplan_name = "test_plan"
        insert_youtube_result(self.session, testplan_name, testplan_data)
        success = insert_youtube_result(self.session, testplan_name, testplan_data)

        self.assertFalse(success)

    def test_insert_youtube_result_duplicate_video(self):
        testplan_name = "test_plan"

        testplan = deepcopy(testplan_data)
        testplan["items"].append(testplan["items"][0])
        success = insert_youtube_result(self.session, testplan_name, testplan_data)

        self.assertTrue(success)

    def test_insert_youtube_result_with_no_all_keys(self):
        testplan_name = "test_plan"
        testplan = deepcopy(testplan_data)
        testplan["args"].pop("relevanceLanguage")
        testplan["args"].pop("topicId")
        testplan["args"].pop("videoCategoryId")
        testplan["args"].pop("videoDuration")

        success = insert_youtube_result(self.session, testplan_name, testplan)
        self.assertFalse(success)
        # it should check if keys exist in db


if __name__ == "__main__":
    unittest.main()
