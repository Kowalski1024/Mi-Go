from typing import Union
from pathlib import Path
import dateutil
import argparse
import time
import json
import os

from youtube_transcript_api import YouTubeTranscriptApi
import googleapiclient.discovery

from testplan_generator.categories import CATEGORIES

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_key = os.environ.get("GoogleAPI")

api_service_name = "youtube"
api_version = "v3"

youtube_api = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)


def videos_details_request(videos: list):
    request = youtube_api.videos().list(
        part="contentDetails,snippet",
        id=','.join(videos)
    )

    return request.execute()


def categories_request(hl: str, region_code: str):
    request = youtube_api.videoCategories().list(
        part="snippet",
        hl=hl,
        regionCode=region_code
    )

    return request.execute()


def search_request(args: dict):
    request = youtube_api.search().list(
        **args,
        part="snippet",
        type="video",
        videoCaption="closedCaption",
    )
    response = request.execute()
    response['videoCategoryId'] = args['videoCategoryId']

    return response


def results_parser(results: dict):
    keys = {'videoId', 'channelId', 'channelTitle', 'publishTime', 'title'}
    for video in results['items']:
        video: dict
        dicts = [value for key, value in video.items() if isinstance(value, dict)]

        for d in dicts:
            video.update(d)

        for key in set(video).difference(keys):
            video.pop(key, None)

    results.pop('kind')
    results.pop('pageInfo')

    return results


def add_video_details(videos):
    video_ids = [video['videoId'] for video in videos]
    response = videos_details_request(video_ids)

    for response_item, video in zip(response['items'], videos):
        language = response_item['snippet'].get('defaultAudioLanguage', None)
        duration = response_item['contentDetails'].get('duration')

        if response_item['id'] == video['videoId']:
            video['defaultAudioLanguage'] = language
            video['duration'] = duration
        else:
            raise KeyError


def add_transcripts_info(items: list):
    for video in items:
        video_id = video['videoId']
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        video['manuallyCreatedTranscripts'] = list(transcripts._manually_created_transcripts.keys())
        video['generatedTranscripts'] = list(transcripts._generated_transcripts.keys())


def category_title_by_language(category_id: int, hl: str, region_code: str = 'US'):
    for category in categories_request(hl, region_code)['items']:
        if category['id'] == category_id:
            return category['snippet'].get('title', None)

    return None


def save_as_json(results: dict, destination: Union[str, os.PathLike]):
    args = results.get('args')
    category_id = int(args.get('videoCategoryId'))
    language = args.get('relevanceLanguage')
    page_token = args.get('pageToken')

    if page_token is None:
        page_token = 'CAUQAQ'

    category = CATEGORIES[category_id].replace(' ', '')
    time_str = time.strftime("%Y%m%d-%H%M%S")

    filename = f'{category}_{language}_{page_token}_{time_str}.json'

    path = Path(destination).joinpath(filename)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4, sort_keys=True)


def command_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=str)
    parser.add_argument('maxResults', type=int)
    parser.add_argument(
        '-l', '--relevanceLanguage',
        required=False, type=str, default='en'
    )
    parser.add_argument(
        '-c', '--videoCategoryId',
        required=False, type=str
    )
    parser.add_argument(
        '-t', '--topicId',
        required=False, type=str
    )
    parser.add_argument(
        '-r', '--regionCode',
        required=False, type=str, default='US'
    )
    parser.add_argument(
        '-d', '--videoDuration',
        required=False, type=str, default='medium', choices=['any', 'long', 'medium', ' short']
    )
    parser.add_argument(
        '-pt', '--pageToken',
        required=False, type=str
    )
    return parser.parse_known_args()


def main():
    args, unknown = command_parser()

    api_args = vars(args)
    dest = api_args.pop('destination')
    api_args['q'] = category_title_by_language(category_id=args.videoCategoryId,
                                               hl=args.relevanceLanguage,
                                               region_code=args.regionCode)

    search_results = search_request(api_args)
    parsed_results = results_parser(search_results)
    parsed_results['args'] = api_args

    items = parsed_results['items']
    add_transcripts_info(items)
    add_video_details(items)

    save_as_json(results=parsed_results, destination=dest)


if __name__ == "__main__":
    main()
