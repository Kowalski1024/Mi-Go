from pathlib import Path
import dataclasses
import re

from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from loguru import logger


from lib.normalizers import title_normalizer


@dataclasses.dataclass
class Video:
    title: str
    videoId: str
    defaultAudioLanguage: str
    generatedTranscripts: list
    manuallyCreatedTranscripts: list

    def download_mp3(self, destination: Path) -> Path:
        title = title_normalizer(self.title)
        url = f'https://www.youtube.com/watch?v={self.videoId}'

        logger.info(f"Downloading... {self.title} as {title}.mp3")
        audio = YouTube(url).streams.filter(only_audio=True).first()
        audio.download(output_path=destination, filename=f'{title}.mp3')

        return destination.joinpath(f'{title}.mp3')

    def youtube_transcript(self, language: str, generated: bool = False) -> str:
        def code(scr: list) -> str:
            r = re.compile(f"{language}|{language}-*")
            return list(filter(r.match, sorted(scr, key=len)))[0]

        transcripts = YouTubeTranscriptApi.list_transcripts(self.videoId)

        if generated:
            language = code(self.generatedTranscripts)
            srt = transcripts.find_generated_transcript(language_codes=[language]).fetch()
        else:
            language = code(self.manuallyCreatedTranscripts)
            srt = transcripts.find_manually_created_transcript(language_codes=[language]).fetch()

        logger.info(f"Downloaded transcript {language}")
        return ' '.join(fragment['text'] for fragment in srt)

    @classmethod
    def from_dict(cls, data: dict) -> 'Video':
        kwargs = [data[key] for key in Video.fields()]
        return cls(*kwargs)

    @classmethod
    def fields(cls):
        return [field.name for field in dataclasses.fields(cls)]

