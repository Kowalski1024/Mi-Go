import dataclasses
import re
from pathlib import Path

from loguru import logger
from youtube_transcript_api import YouTubeTranscriptApi

from libs.normalizers import title_normalizer


@dataclasses.dataclass
class YouTubeVideo:
    """
    Class to represent a YouTube video
    """

    title: str
    videoId: str
    defaultAudioLanguage: str
    generatedTranscripts: list
    manuallyCreatedTranscripts: list

    def download_mp3(self, destination: Path, downloader: str = 'youtube_dl') -> Path:
        """
        Download video as mp3

        Args:
            destination: destination directory
            downloader: downloader to use, either 'youtube_dl' or 'pytube'

        Returns:
            Path to downloaded file
        """

        title = title_normalizer(self.title)
        url = f"https://www.youtube.com/watch?v={self.videoId}"

        logger.info(
            f"Downloading... (videoId={self.videoId}) '{self.title}' as '{title}.mp3'"
        )

        if destination.joinpath(f"{title}.mp3").exists():
            logger.info(f"File '{title}.mp3' already exists, skipping download")
            return destination.joinpath(f"{title}.mp3")

        if downloader == 'youtube_dl':
            import yt_dlp as youtube_dl

            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                'outtmpl': f'{destination}/{title}'
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        else:
            from pytube import YouTube, exceptions

            try:
                audio = YouTube(url).streams.filter(only_audio=True).first()
            except (exceptions.AgeRestrictedError, exceptions.VideoUnavailable, exceptions.VideoPrivate) as e:
                raise ValueError(f"Failed to download '{self.title}': {e}")

            audio.download(output_path=destination, filename=f"{title}.mp3")

        return destination.joinpath(f"{title}.mp3")

    def youtube_transcript(self, language: str, generated: bool = False) -> str:
        """
        Download transcript from YouTube

        Args:
            language: language of transcript
            generated: if True, download generated transcript, otherwise manually created

        Returns:
            Transcript as string
        """

        def _find(scr: list) -> str:
            # find transcript with similar language
            if not scr:
                raise ValueError("Transcripts list is empty")

            if language == "en":
                if "en" in scr:
                    return "en"
                elif "en-GB" in scr:
                    return "en-GB"
                elif "en-US" in scr:
                    return "en-US"

            r = re.compile(f"{language}|{language}-*")
            srt = sorted(scr, key=len)

            matches = list(filter(r.match, srt))

            if not matches:
                raise ValueError(f"No similar language {language} found in {srt}")

            return matches[0]

        transcripts = YouTubeTranscriptApi.list_transcripts(self.videoId)

        if generated:
            language = _find(self.generatedTranscripts)
            srt = transcripts.find_generated_transcript(
                language_codes=[language]
            ).fetch()
        else:
            language = _find(self.manuallyCreatedTranscripts)
            srt = transcripts.find_manually_created_transcript(
                language_codes=[language]
            ).fetch()

        logger.info(f"Downloaded transcript {language}")

        return " ".join(fragment["text"] for fragment in srt)

    @classmethod
    def from_dict(cls, data: dict) -> "YouTubeVideo":
        """
        Create YouTubeVideo object from dict

        Args:
            data: dict with video data

        Returns:
            YouTubeVideo object
        """

        kwargs = [data[key] for key in YouTubeVideo.fields()]

        return cls(*kwargs)

    @classmethod
    def fields(cls):
        """
        Get fields of dataclass
        """

        return [field.name for field in dataclasses.fields(cls)]
