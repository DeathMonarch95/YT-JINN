#!C:\Users\Yash\AppData\Local\Programs\Python\Python312\python.exe

import json
import cgi
import subprocess

print("Content-Type: application/json\n")

form = cgi.FieldStorage()
url = form.getvalue("url")

if not url:
    print(json.dumps({"error": "No URL provided"}))
    exit()

try:
    result = subprocess.run(
        ["yt-dlp", "--dump-json", url],
        capture_output=True, text=True, check=True
    )
    video_info = json.loads(result.stdout)
    output = {
        "title": video_info.get("title"),
        "views": video_info.get("view_count"),
        "uploader": video_info.get("uploader"),
        "upload_date": video_info.get("upload_date"),
        "duration": video_info.get("duration_string", video_info.get("duration")),
        "thumbnail": video_info.get("thumbnail"),
    }
    print(json.dumps(output))
except Exception as e:
    print(json.dumps({"error": str(e)}))
