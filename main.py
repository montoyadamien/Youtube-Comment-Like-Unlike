import argparse
import time
import secrets
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_SECRET_PATH = "secret.json"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MAX_RESULTS = 50
SLEEP_TIME = 30

interactions = 0
videos_passed = 0

def get_youtube_connection():
    flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_SECRET_PATH, SCOPES)
    credentials = flow.run_console()
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)


def get_random_comment(comments):
    return secrets.choice(comments)


def youtube_search(options):
    global interactions
    global videos_passed
    print("=== Initiating api connection ===")
    youtube_api = get_youtube_connection()
    next_page_token = None
    while videos_passed < MAX_RESULTS:
        print("=== Initiating search ===")
        search_response = youtube_api.search().list(
            q=options.query,
            maxResults=options.size,
            part="snippet",
            type="video",
            pageToken=next_page_token
        ).execute()
        next_page_token = search_response.get('nextPageToken')
        for search_result in search_response.get("items", []):
            video_id = search_result["id"]["videoId"]
            print("====== Checking like status for video with id", video_id, "======")
            like_response = youtube_api.videos().getRating(
                id=video_id
            ).execute()
            rating = like_response.get("items", [])[0]["rating"]
            videos_passed += 1
            if rating == "like" or rating == "dislike":
                print("====== Video with id", video_id, "already got a", rating, "=====")
                # video already like so the comment must have already been posted
                continue
            else:
                print("====== Video with id", video_id, "has not been liked or disliked =======")
                if options.comments is not None:
                    print("========= Adding comment to the video with id", video_id, "=========")
                    youtube_api.commentThreads().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "videoId": video_id,
                                "topLevelComment": {
                                    "snippet": {
                                        "textOriginal": get_random_comment(options.comments)
                                    }
                                }
                            }
                        }
                    ).execute()
                print("========= Adding ", options.rating, " to the video with id", video_id, "=========")
                youtube_api.videos().rate(
                    id=video_id,
                    rating=options.rating
                ).execute()
                interactions += 1
                time.sleep(options.sleep)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="Query to search")
    parser.add_argument("--comments", nargs='+', help="Comment to add")
    parser.add_argument("--size", help="Max number of video to search", default=MAX_RESULTS)
    parser.add_argument("--rating", help="Rating to set on the video", default="like")
    parser.add_argument("--sleep", help="Rating to set on the video", default=SLEEP_TIME)
    args = parser.parse_args()

    if args.query is None:
        print("Query must be defined")
        exit(1)

    if args.rating is not None and args.rating != "like" and args.rating != "dislike":
        print("Rating must be like or dislike")
        exit(1)

    try:
        youtube_search(args)
    except HttpError as e:
        print("An HTTP error ", e.resp.status, " occurred:", e.content)
    except KeyboardInterrupt as e:
        print("You have stopped the script")

    print("=== The script got interactions with", interactions, "videos and passed on ", videos_passed, " ===")
