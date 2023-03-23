from typing import Iterable
import argparse
from pathlib import Path
from os import PathLike
import json
import os
import time

from loguru import logger

from lib.youtube_video import YouTubeVideo
from testrunners import TestRunnerBase, TestRegistry
from testrunners.tests.tests import TranscriptDifference
from generators.youtube_generator import generate


@TestRegistry.register(TranscriptDifference)
class YouTubeTestRunner(TestRunnerBase):
    def __init__(self,
                 testplan_path: PathLike,
                 audio_dir: PathLike,
                 transcript_dir: PathLike = None,
                 iterations: int = 1,
                 **kwargs):
        super().__init__(**kwargs)

        self._audio_dir = Path(audio_dir)
        self._transcript_dir = Path(transcript_dir)
        self._testplan_path = Path(testplan_path)
        self._iterations = iterations

    def run(self):
        if self.tester.transcriber is None:
            raise ValueError("Transcriber is None")

        if self.tester.normalizer is None:
            logger.warning("Normalizer is None, running without normalizer")

        if self._iterations > 1 and "GoogleAPI" not in os.environ:
            raise ValueError(
                "GoogleAPI not in the environment, can not generate more test plans. "
                "Add GoogleAPI or set iterations to 1."
            )

        with open(self._testplan_path) as f:
            testplan = json.load(f)

        for i in range(self._iterations):
            logger.info(f"Starting {i + 1}/{self._iterations} testplan")
            logger.info(f"Testplan args: {testplan['args']}, PageToken: ")

            for idx, video_details in enumerate(self.video_details(testplan)):
                logger.info(
                    f"Testplan status: {idx + 1}/{len(testplan['items'])} video, {i + 1}/{self._iterations} testplan"
                )

                video = YouTubeVideo.from_dict(video_details)
                audio = video.download_mp3(self._audio_dir)

                try:
                    model_transcript = self.tester.transcribe(audio)
                except TimeoutError as e:
                    logger.warning(f"Skipping the video {video.videoId}, TimeoutError (model transcript): {e}")
                    video_details['Error'] = f"TimeoutError (model transcript): {e}"
                    continue

                try:
                    target_transcript = video.youtube_transcript(self.tester.language)
                except ValueError as e:
                    logger.warning(f"Skipping the video {video.videoId}, ValueError (youtube transcript): {e}")
                    video_details['Error'] = f"ValueError (youtube transcript): {e}"
                    continue

                results = self.tester.compare(model_transcript, target_transcript)
                video_details['results'] = results

            self.save_results(testplan)
            self.tester.testplan_postprocess(testplan)

            if i+1 < self._iterations:
                args = testplan['args']
                args['pageToken'] = testplan['nextPageToken']
                testplan = generate(args)

    @staticmethod
    def video_details(testplan: dict) -> Iterable[dict]:
        videos = testplan['items']
        for video_details in videos:
            yield video_details

    @classmethod
    def save_results(cls, results):
        time_str = time.strftime("%Y%m%d-%H%M%S")
        filename = f'{cls.__name__}_{time_str}.json'

        path = Path(__file__).parent.joinpath('output', filename)
        path.parent.mkdir(exist_ok=True)

        logger.info(f"Saving results - {path}")

        with open(path, 'x', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    @staticmethod
    def runner_args(parser: argparse.ArgumentParser):
        parser.add_argument(
            type=str, dest='testplan_path',
            help='Testplan path'
        )

        parser.add_argument(
            '-tp', '--transcript-path',
            required=False, type=str, default='./cache/transcript', dest='transcript_dir',
        )

        parser.add_argument(
            '-ap', '--audio-path',
            required=False, type=str, default='./cache/audio', dest="audio_dir"
        )

        parser.add_argument(
            '-it', '--iterations',
            required=False, type=int, default=1
        )


if __name__ == '__main__':
    YouTubeTestRunner.from_command_line().run()
