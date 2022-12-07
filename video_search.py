import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def main():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    key = os.environ.get("GoogleAPI")

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=key)

    request = youtube.search().list(
        part="snippet",
        relevanceLanguage="pl",
        type="video",
        videoCaption="closedCaption",
        videoCategoryId="28"
    )
    response = request.execute()

    print(response)


if __name__ == "__main__":
    main()