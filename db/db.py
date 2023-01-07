import copy
import sqlite3

conn = sqlite3.connect('db.sqlite')

with open('./db/create.sql', 'r') as sql_file, conn:
    sql_script = sql_file.read()
    conn.cursor().executescript(sql_script)


def _sql_insert(table: str, columns: list) -> str:
    return f'''
        INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' * len(columns))})
        '''


def _insert_testplan_basic_data(testplan: dict) -> int:
    testplan = copy.deepcopy(testplan)

    testplan_keys = [
        'nextPageToken',
        'regionCode',
        'videoCategoryId',
        'etag'
    ]

    args_keys = [
        'requestId',
        'maxResults',
        'pageToken',
        'q',
        'videoCategoryId',
        'regionCode',
        'relevanceLanguage',
        'topicId',
        'videoDuration'
    ]

    args = testplan.pop('args')

    with conn:
        cursor = conn.cursor()

        values = [testplan.get(key, None) for key in testplan_keys]
        cursor.execute(_sql_insert('Request', testplan_keys), values)
        row_id = cursor.lastrowid

        values = [args.get(key, None) for key in args_keys]
        cursor.execute(_sql_insert('Args', args_keys), values)

    return row_id


def _insert_video(request_id: int, video: dict) -> int:
    video = copy.deepcopy(video)

    video_keys = [
        'videoId',
        'requestId',
        'defaultAudioLanguage',
        'duration'
    ]

    transcript_keys = [
        'id',
        'lang'
    ]

    video['requestId'] = request_id

    generated_transcripts = video.pop('generatedTranscripts')
    manually_created_transcripts = video.pop('manuallyCreatedTranscripts')

    with conn:
        cursor = conn.cursor()

        values = [video.get(key, None) for key in video_keys]
        cursor.execute(_sql_insert('Video', video_keys), values)
        row_id = cursor.lastrowid

        values = [(row_id, lang) for lang in generated_transcripts]
        cursor.executemany(_sql_insert('GeneratedTranscripts', transcript_keys), values)

        values = [(row_id, lang) for lang in manually_created_transcripts]
        cursor.executemany(_sql_insert('ManuallyCreatedTranscripts', transcript_keys), values)

    return row_id


def insert_transcript_diff_results(testplan: dict):
    testplan = copy.deepcopy(testplan)

    results_keys = [
        'id',
        'wer',
        'matchRatio'
    ]

    replace_keys = [
        'id',
        'model',
        'yt'
    ]

    insert_delete_keys = [
        'id',
        'word',
        'operation'
    ]

    request_id = _insert_testplan_basic_data(testplan)

    for video in testplan['items']:
        video_id = _insert_video(request_id, video)

        results = video.pop('results')
        replace = results.pop('replace')
        insert = results.pop('insert')
        delete = results.pop('delete')

        with conn:
            cursor = conn.cursor()

            values = [results.get(key, None) for key in results_keys]
            cursor.execute(_sql_insert('TranscriptDiffResults', results_keys), values)

            values = [(video_id, model, yt) for model, yt in replace]
            cursor.executemany(_sql_insert('TranscriptDiffReplace', replace_keys), values)

            values = [(video_id, word, 1) for word in insert] + [(video_id, word, -1) for word in delete]
            cursor.executemany(_sql_insert('TranscriptDiffInsertDelete', insert_delete_keys), values)



