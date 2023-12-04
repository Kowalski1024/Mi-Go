from typing import Any, Mapping

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.youtube import YouTubeResult, YouTubeTestPlan, YouTubeVideo


def insert_youtube_result(
    session: Session, testplan_name: str, testplan: Mapping[str, Any]
) -> bool:
    try:
        testplan_obj = YouTubeTestPlan.from_testplan(testplan_name, testplan)
        session.add(testplan_obj)
        session.flush()
        session.refresh(testplan_obj)
    except IntegrityError:
        return False

    testplan_id = testplan_obj.id

    for video in testplan["items"]:
        video_id = video["videoId"]

        if session.query(YouTubeVideo).filter(YouTubeVideo.video_id == video_id).count() == 0:
            video_obj = YouTubeVideo.from_video(video)
            session.add(video_obj)

        if "results" not in video:
            continue

        results_obj = YouTubeResult.from_result(testplan_id, video_id, video["results"])
        session.add(results_obj)

    session.commit()
    return True
