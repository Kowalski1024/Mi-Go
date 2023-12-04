from typing import Any, Mapping

import numpy as np
from sqlalchemy import Column, Float, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import declarative_base

YouTubeBase = declarative_base()


class YouTubeTestPlan(YouTubeBase):
    __tablename__ = "youtube_testplan"
    id = Column(Integer, Sequence("youtube_id_seq"), primary_key=True)

    # Query arguments
    max_results = Column(Integer)
    page_token = Column(String)
    q = Column(String)
    region_code = Column(String)
    relevance_language = Column(String)
    topic_id = Column(String)
    video_category_id = Column(String)
    video_duration = Column(String)
    video_license = Column(String)

    # Additional information
    testplan_name = Column(String, unique=True)
    etag = Column(String)
    next_page_token = Column(String)
    total_results = Column(Integer)
    success = Column(Integer)

    # Statistics
    std = Column(Float)
    mean = Column(Float)

    @classmethod
    def from_testplan(cls, testplan_name: str, testplan: Mapping[str, Any]) -> "YouTubeTestPlan":
        args = testplan["args"]
        success = [items for items in testplan["items"] if "results" in items]

        if success:
            wer_array = np.array([items["results"]["wer"] for items in success])
        else:
            wer_array = np.array([0])

        return cls(
            max_results=args["maxResults"],
            page_token=args["pageToken"],
            q=args["q"],
            region_code=args["regionCode"],
            relevance_language=args["relevanceLanguage"],
            topic_id=args["topicId"],
            video_category_id=args["videoCategoryId"],
            video_duration=args["videoDuration"],
            video_license=args["videoLicense"],
            testplan_name=testplan_name,
            etag=testplan["etag"],
            next_page_token=testplan["nextPageToken"],
            total_results=len(testplan["items"]),
            success=len(success),
            std=np.std(wer_array),
            mean=np.mean(wer_array),
        )


class YouTubeVideo(YouTubeBase):
    __tablename__ = "youtube_video"

    video_id = Column(String, primary_key=True)
    title = Column(String)
    channel_id = Column(String)
    channel_title = Column(String)
    default_audio_language = Column(String)
    duration = Column(String)
    publish_time = Column(String)

    @classmethod
    def from_video(cls, video: Mapping[str, Any]) -> "YouTubeVideo":
        return cls(
            video_id=video["videoId"],
            title=video["title"],
            channel_id=video["channelId"],
            channel_title=video["channelTitle"],
            default_audio_language=video["defaultAudioLanguage"],
            duration=video["duration"],
            publish_time=video["publishTime"],
        )


class YouTubeResult(YouTubeBase):
    __tablename__ = "youtube_result"
    id = Column(Integer, Sequence("youtube_id_seq"), primary_key=True)

    testplan_id = Column(Integer, ForeignKey("youtube_testplan.id"))
    model_name = Column(String)
    language = Column(String)

    video_id = Column(String, ForeignKey("youtube_video.video_id"))

    wer = Column(Float)
    mer = Column(Float)
    wil = Column(Float)
    wip = Column(Float)

    hits = Column(Integer)
    substitutions = Column(Integer)
    deletions = Column(Integer)
    insertions = Column(Integer)

    model_settings = Column(String)

    @classmethod
    def from_result(
        cls, testplan_id: int, video_id: str, result: Mapping[str, Any]
    ) -> "YouTubeResult":
        return cls(
            testplan_id=testplan_id,
            video_id=video_id,
            model_name=result["modelName"],
            language=result["language"],
            wer=result["wer"],
            mer=result["mer"],
            wil=result["wil"],
            wip=result["wip"],
            hits=result["hits"],
            substitutions=result["substitutions"],
            deletions=result["deletions"],
            insertions=result["insertions"],
            model_settings=result.get("modelSettings", None),
        )
