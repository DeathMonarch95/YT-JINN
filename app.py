from flask import Flask, request, jsonify, render_template
import requests
import re

app = Flask(__name__)

API_KEY = 'AIzaSyBhadU45U3_64K_csW1oQEZJtiQwSUjRXw'  # <-- Put your YouTube API key here

def extract_video_id(url_or_id):
    """
    Extract YouTube video ID from URL or return if already an ID
    """
    # regex to match YouTube video IDs in URLs
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # e.g. youtube.com/watch?v=ID or youtu.be/ID
    ]
    for pat in patterns:
        m = re.search(pat, url_or_id)
        if m:
            return m.group(1)
    return url_or_id  # if no match, assume input is ID

def get_video_info(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={video_id}&key={API_KEY}"
    res = requests.get(url)
    data = res.json()
    if 'items' not in data or not data['items']:
        return None

    video = data['items'][0]
    snippet = video.get('snippet', {})
    stats = video.get('statistics', {})
    content_details = video.get('contentDetails', {})

    # channel info
    channel_id = snippet.get('channelId', '')
    channel_info = get_channel_info(channel_id)

    # related videos from same channel
    related = get_related_videos(channel_id)

    return {
        "title": snippet.get('title', 'No title'),
        "description": snippet.get('description', ''),
        "views": int(stats.get('viewCount', 0)),
        "likes": int(stats.get('likeCount', 0)) if 'likeCount' in stats else None,
        "upload_date": snippet.get('publishedAt', ''),
        "duration": content_details.get('duration', ''),
        "thumbnail": snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
        "channel_name": snippet.get('channelTitle', ''),
        "channel_thumbnail": channel_info.get('thumbnail', ''),
        "channel_subscribers": channel_info.get('subscribers', 0),
        "related": related
    }

def get_channel_info(channel_id):
    if not channel_id:
        return {}
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={API_KEY}"
    res = requests.get(url)
    data = res.json()
    if 'items' not in data or not data['items']:
        return {}

    ch = data['items'][0]
    snippet = ch.get('snippet', {})
    stats = ch.get('statistics', {})

    return {
        "thumbnail": snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
        "subscribers": int(stats.get('subscriberCount', 0)),
    }

def get_related_videos(channel_id, max_results=5):
    if not channel_id:
        return []
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults={max_results}&order=date&type=video&key={API_KEY}"
    res = requests.get(url)
    data = res.json()
    related = []
    for item in data.get('items', []):
        if item.get('id', {}).get('kind') == 'youtube#video':
            snippet = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId')
            related.append({
                "video_id": video_id,
                "title": snippet.get('title', ''),
                "thumbnail": snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                "views": 'N/A',   # views/likes not provided here; you can enhance by fetching each video's stats if needed
                "likes": 'N/A'
            })
    return related

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video-info')
def video_info():
    video_param = request.args.get('video_id', '')
    video_id = extract_video_id(video_param)
    info = get_video_info(video_id)
    if not info:
        return jsonify({"error": "Video not found"}), 404
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
