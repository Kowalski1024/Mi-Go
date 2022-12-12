from typing import Union, Optional, Iterable, Callable
from pathlib import Path
from os import PathLike
import argparse
import json
import time

from loguru import logger

from lib.video import Video


class TestBase:
    def __init__(self,
                 testplan_file: Union[str, PathLike],
                 audio_path: Union[str, PathLike],
                 transcript_path: Union[str, PathLike] = None,
                 ) -> None:

        self.audio_path = Path(audio_path)
        self._transcript_path = Path(transcript_path)

        self._testplan_path = testplan_file

        with open(testplan_file) as f:
            self._testplan = json.load(f)

        self.transcriber: Optional[Callable] = None
        self.normalizer: Optional[Callable] = None

    @classmethod
    def from_command_line(cls):
        args, unknown = cls._parse_command()
        return cls(**vars(args))

    def run(self):
        if self.transcriber is None:
            raise ValueError("Transcriber is None")

        if self.normalizer is None:
            logger.warning("Normalizer is None, running without normalizer")

        try:
            for video_details in self.video_details:
                results = self.test_video(video_details)
                video_details['results'] = results

        except TimeoutError:
            pass

        self.add_test_details(self._testplan)

        import pprint
        pprint.pprint(self._testplan)
        self.save_results(self._testplan)

    def test_video(self, video_details: dict) -> dict:
        raise NotImplementedError

    @property
    def video_details(self) -> Iterable[dict]:
        videos = self._testplan['items']
        for video_details in videos:
            yield video_details

    def transcribe(self, audio_path: Path, remove_audio: bool = True, **kwargs) -> dict:
        result = self.transcriber(audio=str(audio_path), **kwargs)

        if remove_audio:
            audio_path.unlink()

        return result

    def normalize(self, string: str) -> str:
        return self.normalizer(string)

    def save_transcript(self, data: dict, filename: str) -> None:
        time_str = time.strftime("%Y%m%d-%H%M%S")
        file = f'{filename}_{time_str}.json'
        path = self._transcript_path.joinpath(file)

        if path.is_file():
            logger.warning(f'File {file} already exists')
            return

        path.parent.mkdir(exist_ok=True)

        with open(path, 'x', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_test_details(self, results: dict):
        pass

    @classmethod
    def save_results(cls, results):
        time_str = time.strftime("%Y%m%d-%H%M%S")
        path = Path(__file__).parent.joinpath('output', f'{cls.__name__}_{time_str}.json')
        path.parent.mkdir(exist_ok=True)

        with open(path, 'x', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        pass

    @classmethod
    def _parse_command(cls):
        parser = argparse.ArgumentParser()
        cls.add_arguments(parser)

        parser.add_argument(
            type=str, dest='testplan_file'
        )
        parser.add_argument(
            '-tp', '--transcript-path',
            required=False, type=str, default='./cache/transcript', dest='transcript_path'
        )
        parser.add_argument(
            '-ap', '--audio-path',
            required=False, type=str, default='./cache/audio', dest="audio_path"
        )

        return parser.parse_known_args()
