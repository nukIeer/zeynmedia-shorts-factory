import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _youtube():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload_video(path, yt_meta, privacy="public", category_id="17"):
    body = {
        "snippet": {
            "title": yt_meta["title"],
            "description": yt_meta["description"],
            "tags": yt_meta["tags"],
            "categoryId": category_id,
            "defaultLanguage": os.environ.get("CONTENT_LANG", "tr"),
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(path), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    request = _youtube().videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[upload] %{int(status.progress() * 100)}")
    video_id = response["id"]
    print(f"[upload] yüklendi: https://youtube.com/shorts/{video_id}")
    return video_id
