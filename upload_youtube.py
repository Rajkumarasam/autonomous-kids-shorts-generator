import argparse, os, json
import boto3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_yt_creds():
    # Retrieve refresh token from AWS Secrets Manager
    secrets = boto3.client('secretsmanager', region_name='us-east-1')
    try:
        secret = secrets.get_secret_value(SecretId='YOUTUBE_REFRESH_TOKEN')
        creds_data = json.loads(secret['SecretString'])
        creds = Credentials.from_authorized_user_info(creds_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Auth failed: {e}")
        return None

def upload(title):
    creds = get_yt_creds()
    if not creds: return
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    print(f"📤 Uploading: {title}")
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "A magical adventure for kids! Subscribe for daily stories! #shorts #kids #animation",
                "categoryId": "27", # Education
                "tags": ["kids", "animation", "shorts", "adventure"]
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": True
            }
        },
        media_body=MediaFileUpload("/tmp/final_shorts.mp4", resumable=True)
    )
    response = request.execute()
    print(f"✅ Uploaded! ID: {response['id']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    upload(args.title)
