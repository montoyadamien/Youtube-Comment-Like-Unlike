# YouTube comment, like or unlike bot

##  Goals

This project allows you to add comment, like or dislike YouTube videos based on a query.  
If a video has already been liked or disliked, the script will just skip it and will not add comment on it.

## YouTube limitations

Note that YouTube will limit the number of comments, like or dislike or query you can send and a 403 error will be raised when this limit is reached. More information [here](https://developers.google.com/youtube/v3/getting-started#quota).

## Run the bot
- First of all you need to set up a [Google Cloud Console](https://console.cloud.google.com/?hl=fr) project (it is free)
- Then create an Oauth 2.0 credential
- Next you will have to download the oauth credentials files in the project folder and name it `secret.json`
- Install [Python](https://www.python.org/downloads/)
- Install the requirements with the command `pip install -r requirements.txt`
- Run the script with the following command `python main.py --query "my query" [--comments "My comment" "My other comment" --rating like --size 50 --sleep 20]`
  - --query
    - The query to search videos
    - mandatory
    - value: any text
  - --comments
    - The different comments to randomly add on each video. When adding a comment on a video, only one will be selected randomly.
    - optional
    - value: any text
  - --rating
    - Whether to like or dislike the video
    - optional
    - value: like | dislike
    - default: like
  - --size
    - The number of videos to query
    - optional
    - value: any positive integer
    - default: 50 (min 0, no max)
  - --sleep
    - The pause time in seconds between each like/dislike/comment (useful to get a long time running script without exceed YouTube quota)
    - optional
    - value: any positive integer
    - default: 30
  - --region
    - Specify the region that should be allowed for the video
    - optional
    - value: any two length country code
- The script will then ask you to open your browser in order to grant you a Google access token
- Authorize things and copy the token that Google returns you
- Paste the token in the console
- Like or dislike as many video as you wish, but please, be kind in your comments 🙂

## Documentation
- [YouTube Api V3](https://developers.google.com/youtube/v3/docs)