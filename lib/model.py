from typing import Union, Optional
import json
from pathlib import Path
from os import PathLike

import whisper


class Model:
    def __init__(self,
                 model: whisper.Whisper,
                 model_type: str,
                 transcript_path: Union[str, PathLike],
                 cache: bool = True,
                 clear: bool = False
                 ) -> None:

        self.model_type = model_type.replace('.', '-')
        self.model = model
        self.cache = cache
        self.transcript_path = Path(transcript_path)
        self.clear = clear

    def load(self, filename: str) -> dict:
        path = self.transcript_path.joinpath(f'{filename}_{self.model_type}.json')
        with open(path) as f:
            return dict(json.load(f))

    def save(self, data, filename: str) -> None:
        path = self.transcript_path.joinpath(f'{filename}_{self.model_type}.json')

        if path.is_file():
            raise FileExistsError('File already exists')

        with open(path, 'x', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def transcribe(self, audio_path: Path, delete_audio: Optional[bool] = None, **kwargs) -> dict:
        filename = audio_path.stem
        transcript_path = self.transcript_path.joinpath(f'{filename}_{self.model_type}.json')

        if self.cache and transcript_path.is_file():
            return self.load(filename)

        result = self.model.transcribe(audio='.' + str(audio_path), **kwargs)

        if self.cache:
            self.save(result, filename)

        if delete_audio:
            audio_path.unlink()

        return result
