from pathlib import Path
import dataclasses

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

        logger.info(f"Start download... {self.title} as {title}.mp3")
        audio = YouTube(url).streams.filter(only_audio=True).first()
        audio.download(output_path=destination, filename=f'{title}.mp3')

        return destination.joinpath(f'{title}.mp3')

    def youtube_transcript(self, language: str, generated: bool = False) -> str:
        transcripts = YouTubeTranscriptApi.list_transcripts(self.videoId)

        if generated:
            srt = transcripts.find_generated_transcript(language_codes=[language]).fetch()
        else:
            srt = transcripts.find_manually_created_transcript(language_codes=[language]).fetch()

        return ' '.join(fragment['text'] for fragment in srt)

    @classmethod
    def from_dict(cls, data: dict) -> 'Video':
        kwargs = [data[key] for key in Video.fields()]
        return cls(*kwargs)

    @classmethod
    def fields(cls):
        return [field.name for field in dataclasses.fields(cls)]

