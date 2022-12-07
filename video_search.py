import argparse
import os
import pprint

from youtube_transcript_api import YouTubeTranscriptApi
import googleapiclient.discovery
import googleapiclient.errors


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_key = os.environ.get("GoogleAPI")

api_service_name = "youtube"
api_version = "v3"

youtube_api = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)


def videos_details_request(videos: list):
    request = youtube_api.videos().list(
        part="snippet",
        id=','.join(videos)
    )

    return request.execute()


def search_request(args: dict):
    request = youtube_api.search().list(
        **args,
        part="snippet",
        type="video",
        videoCaption="closedCaption"
    )
    response = request.execute()
    response['videoCategoryId'] = args['videoCategoryId']
    return response


def results_parser(results: dict):
    keys = {'etag', 'videoId', 'channelId', 'channelTitle', 'publishTime', 'title'}
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


def default_language(videos):
    video_ids = [video['videoId'] for video in videos]
    response = videos_details_request(video_ids)

    for response_item, video in zip(response['items'], videos):
        language = response_item['snippet'].get('defaultAudioLanguage', None)
        if response_item['id'] == video['videoId']:
            video['defaultAudioLanguage'] = language
        else:
            raise KeyError


def transcripts_info(items):
    for video in items:
        video_id = video['videoId']
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        video['manually_created_transcripts'] = list(transcripts._manually_created_transcripts.keys())
        video['generated_transcripts'] = list(transcripts._generated_transcripts.keys())


def command_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=str)
    parser.add_argument('maxResults', type=int)
    parser.add_argument('-l', '--relevanceLanguage', required=False, type=str)
    parser.add_argument('-c', '--videoCategoryId', required=False, type=str)
    parser.add_argument('-r', '--regionCode', required=False, type=str)
    parser.add_argument('-t', '--topicId', required=False, type=str)
    return parser.parse_known_args()


def main():
    args, unknown = command_parser()
    api_args = vars(args)
    api_args.pop('destination')
    api_args.pop('fileName')
    search_results = search_request(api_args)
    parsed_results = results_parser(search_results)

    items= parsed_results['items']
    transcripts_info(items)
    default_language(items)

    pprint.pprint(parsed_results)


if __name__ == "__main__":
    main()
