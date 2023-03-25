from pathlib import Path
from functools import lru_cache
import pprint
import argparse
import time
import json
import os

from youtube_transcript_api import YouTubeTranscriptApi
from loguru import logger
import googleapiclient.discovery

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_key = os.environ.get("GoogleAPI")

api_service_name = "youtube"
api_version = "v3"

youtube_api = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)


def videos_details_request(videos: list):
    logger.info("Request videos details")
    request = youtube_api.videos().list(
        part="contentDetails,snippet",
        id=','.join(videos)
    )

    return request.execute()


@lru_cache
def categories_request(hl: str, region_code: str):
    logger.info("Request categories")
    request = youtube_api.videoCategories().list(
        part="snippet",
        hl=hl,
        regionCode=region_code
    )

    return request.execute()


def assignable_categories(hl: str, region_code: str) -> dict[int, str]:
    results = categories_request(hl, region_code)
    return {int(res['id']): res['snippet']['title'] for res in results['items'] if res['snippet']['assignable']}


def search_request(args: dict, part: str = "snippet", video_type: str = "video", caption: str = "closedCaption"):
    logger.info(f"Request search with args: part={part}, type={video_type}, videoCaption={caption} and {args}")
    request = youtube_api.search().list(
        **args,
        part=part,
        type=video_type,
        videoCaption=caption,
    )
    response = request.execute()
    response['videoCategoryId'] = args['videoCategoryId']

    return response


def results_parser(results: dict):
    logger.info("Parsing results")
    keys = {'videoId', 'channelId', 'channelTitle', 'publishTime', 'title'}

    if n := len(results['items']):
        logger.info(f"{n} results found")
    else:
        logger.error(f"{n} results found")

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
    logger.info("Adding transcript info")
    for video in items:
        video_id = video['videoId']
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        video['manuallyCreatedTranscripts'] = list(transcripts._manually_created_transcripts.keys())
        video['generatedTranscripts'] = list(transcripts._generated_transcripts.keys())


def save_as_json(results: dict, destination: os.PathLike, category: str):
    args = results.get('args')
    language = args.get('relevanceLanguage')
    page_token = args.get('pageToken')

    if page_token is None:
        page_token = 'CAUQAQ'

    category = category.replace(' ', '')
    time_str = time.strftime("%Y%m%d-%H%M%S")

    filename = f'{category}_{language}_{page_token}_{time_str}.json'

    path = Path(destination).joinpath(filename)
    path.parent.mkdir(exist_ok=True)

    logger.info(f"Saving results to json file at {path}")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4, sort_keys=True)


def command_parser():
    parser = argparse.ArgumentParser(prog="Testplan generator", description="Generating json files used as testplan")
    parser.add_argument('maxResults', type=int)
    parser.add_argument(
        '-o', '--outputDirectory',
        required=False, type=str, default='./testplans/',
        help='Destination of the testplan'
    )
    parser.add_argument(
        '-l', '--relevanceLanguage',
        required=False, type=str, default='en',
        help='Preferred language'
    )
    parser.add_argument(
        '-c', '--videoCategoryId',
        required=False, type=str,
        help='Video category id, see categories.py'
    )
    parser.add_argument(
        '-t', '--topicId',
        required=False, type=str,
    )
    parser.add_argument(
        '-r', '--regionCode',
        required=False, type=str, default='US',
    )
    parser.add_argument(
        '-d', '--videoDuration',
        required=False, type=str, default='medium', choices=['any', 'long', 'medium', ' short']
    )
    parser.add_argument(
        '-q', '--queryTerm',
        required=False, type=str, dest='q'
    )
    parser.add_argument(
        '-pt', '--pageToken',
        required=False, type=str,
    )
    return parser.parse_known_args()


def generate(args: dict) -> dict:
    logger.info(f"Generating with args: {args}")
    search_results = search_request(args)
    parsed_results = results_parser(search_results)

    parsed_results['args'] = args

    items = parsed_results['items']
    add_transcripts_info(items)
    add_video_details(items)

    return parsed_results


def main():
    args, unknown = command_parser()

    api_args = vars(args)
    dest = api_args.pop('outputDirectory')
    categories = assignable_categories(hl=args.relevanceLanguage, region_code=args.regionCode)
    category_id = int(args.videoCategoryId)

    if category_id not in categories:
        raise ValueError(f"CategoryId {category_id} is not assignable, available categories:\n"
                         f"{pprint.pformat(categories)}"
                         )

    if api_args.get('queryTerm', None) is None:
        api_args['q'] = categories.get(category_id, None)

    search_results = generate(api_args)

    save_as_json(results=search_results, destination=dest, category=categories[category_id])


if __name__ == "__main__":
    main()
