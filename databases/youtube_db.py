from typing import Callable
import copy
import sqlite3

from loguru import logger

from libs.differs import difflib_differ, jiwer_differ


conn = sqlite3.connect("databases.sqlite")

# Create tables
with open("./databases/youtube_create.sql", "r") as sql_file, conn:
    sql_script = sql_file.read()
    conn.cursor().executescript(sql_script)


def _sql_insert(table: str, columns: list) -> str:
    # Create sql insert statement

    logger.debug(f"Creating sql insert statement for {table} with columns {columns}")
    return f"""
        INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' * len(columns))})
        """


def _insert_testplan_basic_data(testplan: dict) -> int:
    logger.info(f"Inserting testplan")
    # Insert basic data about testplan
    testplan = copy.deepcopy(testplan)

    # Keys for testplan table
    testplan_keys = ["nextPageToken", "regionCode", "videoCategoryId", "etag"]

    args_keys = [
        "requestId",
        "maxResults",
        "pageToken",
        "q",
        "videoCategoryId",
        "regionCode",
        "relevanceLanguage",
        "topicId",
        "videoDuration",
    ]

    args = testplan.pop("args")

    with conn:
        cursor = conn.cursor()

        values = [testplan.get(key, None) for key in testplan_keys]
        cursor.execute(_sql_insert("Request", testplan_keys), values)
        row_id = cursor.lastrowid

        values = [args.get(key, None) for key in args_keys]
        cursor.execute(_sql_insert("Args", args_keys), values)

    return row_id


def _insert_video(request_id: int, video: dict) -> int:
    logger.info(f"Inserting video {video['videoId']}")
    # Insert video data
    video = copy.deepcopy(video)

    # Keys for video table
    video_keys = ["videoId", "requestId", "defaultAudioLanguage", "duration"]

    transcript_keys = ["id", "lang"]

    video["requestId"] = request_id

    generated_transcripts = video.pop("generatedTranscripts")
    manually_created_transcripts = video.pop("manuallyCreatedTranscripts")

    with conn:
        cursor = conn.cursor()

        values = [video.get(key, None) for key in video_keys]
        cursor.execute(_sql_insert("Video", video_keys), values)
        row_id = cursor.lastrowid

        values = [(row_id, lang) for lang in generated_transcripts]
        cursor.executemany(_sql_insert("GeneratedTranscripts", transcript_keys), values)

        values = [(row_id, lang) for lang in manually_created_transcripts]
        cursor.executemany(
            _sql_insert("ManuallyCreatedTranscripts", transcript_keys), values
        )

    return row_id


def _difflib_results(results: dict, video_id: int) -> None:
    logger.info(f"Inserting results using difflib")
    # Keys for results table
    results_keys = ["id", "wer", "matchRatio", "detectedLanguage"]

    replace_keys = ["id", "model", "yt"]

    insert_delete_keys = ["id", "word", "operation"]

    # Remove keys that are not in results table
    replace = results.pop("replace")
    insert = results.pop("insert")
    delete = results.pop("delete")

    with conn:
        cursor = conn.cursor()

        values = (video_id,) + tuple(
            val for key, val in results.items() if key in results_keys
        )
        cursor.execute(_sql_insert("DiffLibResults", results_keys), values)

        values = [(video_id, model, yt) for model, yt in replace]
        cursor.executemany(
            _sql_insert("DiffLibReplace", replace_keys), values
        )

        values = [(video_id, word, 1) for word in insert] + [
            (video_id, word, -1) for word in delete
        ]
        cursor.executemany(
            _sql_insert("DiffLibInsertDelete", insert_delete_keys), values
        )


def _jiwer_results(results: dict, video_id: int) -> None:
    logger.info(f"Inserting results using jiwer")
    # Keys for results table
    results_keys = ["id", "wer", "mer", "wil", "wip", "hits", "substitutions", "deletions", "insertions", "detectedLanguage"]

    with conn:
        cursor = conn.cursor()

        values = (video_id,) + tuple(
            val for key, val in results.items() if key in results_keys
        )
        cursor.execute(_sql_insert("JiwerResults", results_keys), values)


def insert_transcript_diff_results(testplan: dict, differ: Callable) -> None:
    """
    Insert transcript diff results to database

    Args:
        testplan: testplan to insert
    """

    testplan = copy.deepcopy(testplan)

    # Insert basic data about testplan
    request_id = _insert_testplan_basic_data(testplan)

    # Insert additional data
    with conn:
        cursor = conn.cursor()

        model = testplan["model"]

        cursor.execute(
            _sql_insert("TranscriptDiffAdditional", ["requestId", "model", "language", "werMean", "werStd"]),
            (request_id, model["name"], model.get("language", None), model["werMean"], model["werStd"]),
        )

    for video in testplan["items"]:
        # Skip videos with errors
        if e := video["results"].get("error", None):
            logger.warning(f"Skipping inserting results for video {video['videoId']}: {e}")
            continue

        # Insert video data
        video_id = _insert_video(request_id, video)
        results = video.pop("results")

        if differ == difflib_differ:
            _difflib_results(results, video_id)

        elif differ == jiwer_differ:
            _jiwer_results(results, video_id)
