from typing import Union, Optional
import json
from pathlib import Path
from os import PathLike

from tests.test_base import TestBase


class TranscriptDiffTest(TestBase):
    def __init__(self,
                 model_type: str,
                 transcript_path: Union[str, PathLike],
                 audio_path: Union[str, PathLike],
                 audio_links: list[str],
                 cache: bool = True,
                 clear: bool = False
                 ):
        super().__init__(model_type, transcript_path, audio_path, audio_links, cache, clear)
