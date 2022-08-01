import argparse
import time
import secrets
import json
from googleapiclient.errors import HttpError
from youtubeapi import YoutubeApi
from os.path import exists

VIDEO_IDS_FILE = "video_interaction.json"

interactions_number = 0
videos_passed_number = 0
videos_done = {
    "data": []
}

youtube_api_helper = None


def is_video_already_interacted(video_id):
    for x in videos_done["data"]:
        if x["id"] == video_id:
            return True
    return False


def get_random_comment(comments):
    return secrets.choice(comments)


def add_comment(video_id, comments, interactions_with_video):
    if comments is not None:
        print("========= Adding comment to the video with id", video_id, "=========")
        try:
            youtube_api_helper.add_comment(video_id, get_random_comment(comments))
            interactions_with_video.append("comment")
        except HttpError as error:
            if youtube_api_helper.is_forbidden_action_error(error):
                interactions_with_video.append("comment_forbidden")
                print("========= Comment can not be posted on video with id", video_id, "=========")
            else:
                print('========= Unknown error occurred during comment =========')
                raise error


def add_like(video_id, rating, interactions_with_video):
    print("========= Adding ", rating, " to the video with id", video_id, "=========")
    try:
        youtube_api_helper.add_rating(video_id, rating)
        interactions_with_video.append(rating)
    except HttpError as error:
        if YoutubeApi.is_forbidden_action_error(error):
            interactions_with_video.append(rating + "_forbidden")
            print("========= Comment can not be posted on video with id", video_id, "=========")
        else:
            print('========= Unknown error occurred during rating =========')
            raise error


def youtube_search(options):
    global interactions_number
    global videos_passed_number
    print("=== Initiating api connection ===")
    next_page_token = None
    while videos_passed_number < int(options.size):
        print("=== Initiating search ===")
        search_response = youtube_api_helper.make_search(next_page_token, options.query)
        next_page_token = search_response.get('nextPageToken')
        for search_result in search_response.get("items", []):
            videos_passed_number += 1
            video_id = search_result["id"]["videoId"]
            print("====== Checking like status for video with id", video_id, "======")
            if is_video_already_interacted(video_id):
                print("====== Video with id", video_id, "already got interaction =====")
                continue
            interactions_with_video = []
            like_response = youtube_api_helper.is_video_liked_or_unliked(video_id)
            rating = like_response.get("items", [])[0]["rating"]
            if rating == "like" or rating == "dislike":
                print("====== Video with id", video_id, "already got a", rating, "=====")
                interactions_with_video.append(rating)
            else:
                print("====== Video with id", video_id, "has not been liked or disliked =======")
                add_comment(video_id, options.comments, interactions_with_video)
                add_like(video_id, options.rating, interactions_with_video)
                interactions_number += 1
                time.sleep(options.sleep)
            videos_done["data"].append({
                "id": video_id,
                "interactions": interactions_with_video
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="Query to search")
    parser.add_argument("--comments", nargs='+', help="Comments to add")
    parser.add_argument("--size", help="Max number of video to search", default=50)
    parser.add_argument("--rating", help="Rating to set on the video", default="like")
    parser.add_argument("--sleep", help="Sleep time during each interactions", default=30)
    parser.add_argument("--region", help="Country code allowed for the videos")
    args = parser.parse_args()

    if args.query is None:
        print("Query must be defined")
        exit(1)

    if args.rating is not None and args.rating != "like" and args.rating != "dislike":
        print("Rating must be like or dislike")
        exit(1)

    if exists(VIDEO_IDS_FILE):
        file = open(VIDEO_IDS_FILE, "r")
        videos_done = json.loads(file.read())
        file.close()

    youtube_api_helper = YoutubeApi(args.size, args.region)

    try:
        youtube_search(args)
    except HttpError as e:
        print("An HTTP error ", e.resp.status, " occurred:", e.content)
    except KeyboardInterrupt:
        print("You have stopped the script")

    print("=== The script got interactions with", interactions_number, "videos and passed on ", videos_passed_number,
          " ===")
    file = open(VIDEO_IDS_FILE, "w")
    file.write(json.dumps(videos_done, indent=4))
    file.close()
