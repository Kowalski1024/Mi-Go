from typing import Union
from os import PathLike
from pathlib import Path

from pytube import YouTube
from loguru import logger


class Video(YouTube):
    def __init__(self, url: str, audio_path: Union[str, PathLike]):
        super().__init__(url)
        self._audio_path = Path(audio_path)

    def download_mp3(self):
        logger.info(f"Start download... {self.title}")
        audio = self.streams.filter(only_audio=True).first()
        audio.download(output_path=self._audio_path)
        return audio.default_filename
