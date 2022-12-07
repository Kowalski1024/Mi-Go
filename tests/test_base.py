from typing import Union, Optional, Iterable
import json
import argparse
from pathlib import Path
from os import PathLike

import whisper

from lib.model import Model
from lib.video import Video


MODEL_TYPES = [
    'tiny',
    'base',
    'small',
    'medium',
    'large',
    'tiny.en',
    'base.en',
    'small.en',
    'medium.en'
]


class TestBase:
    def __init__(self) -> None:
        args, unknown = self._parse_command()

        self.model_type = args['model-type']
        self.task_manifest = args['task-manifest']
        self.transcript_path = transcript_path
        self.audio_path = audio_path
        self.audio_links = audio_links
        self.cache = cache
        self.clear = clear

        whisper_kwargs = kwargs.get('whisper', None)
        self.whisper = whisper.load_model(model_type, whisper_kwargs)
        self.model = Model(self.whisper, self.model_type, self.transcript_path, cache=self.cache, clear=self.clear)

    def audio_files(self) -> Iterable:
        for link in self.audio_links:
            video = Video(link, self.audio_path)
            yield video.download_mp3()

    def run(self):
        self.set_params()

    def set_params(self):
        args, unknown = self._parse_command()

        self.model_type = args['model-type']
        self.task_manifest = args['task-manifest']
        self.transcript_path = args['transcript-path']
        self.audio_path = args['audio-path']
        self.cache = args['cache']
        self.clear = args['clear']

    @classmethod
    def from_args(cls):
        args, unknown = cls._parse_command()

        model_type = args['model-type']
        task_manifest = args['task-manifest']
        transcript_path = args['transcript-path']
        audio_path = args['audio-path']
        cache = args['cache']
        clear = args['clear']

    @staticmethod
    def _parse_command():
        parser = argparse.ArgumentParser()
        parser.add_argument('video-links', required=True, type=str)
        parser.add_argument('model-type', required=True, choices=MODEL_TYPES)

        parser.add_argument('-tp', '--transcript-path', required=False, type=str, default='./cache/transcript')
        parser.add_argument('-ap', '--audio-path', required=False, type=str, default='./cache/audio')
        parser.add_argument('-cr', '--clear', required=False, action='store_true', default=True)
        parser.add_argument('-c', '--cache', required=False, action='store_true', default=True)

        return parser.parse_known_args()

