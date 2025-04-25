from youtube_transcript_api import YouTubeTranscriptApi
from fastapi import FastAPI, Query, Request
from pydantic import BaseModel
from pytube import YouTube
import subprocess
import yt_dlp
import json
import os

app = FastAPI()

class TranscriptRequest(BaseModel):
    url: str

@app.post("/get-transcript")
def extract_transcript(data: TranscriptRequest):
    try:
        video_id = data.url.split("v=")[-1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = "\n".join([entry["text"] for entry in transcript])

        os.makedirs("transcripts", exist_ok=True)
        path = f"transcripts/{video_id}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

        return { "file": path }
    except Exception as e:
        return {"error": str(e)}

@app.post("/get-video-info")
def get_video_info(data: TranscriptRequest):
    try:
        # 使用 yt_dlp 抓 metadata
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=False)
            title = info.get("title")
            thumbnail_url = info.get("thumbnail")

            # 若為 .webp，則強制轉為 .jpg 版本（部分影片可行）
            if thumbnail_url and "vi_webp" in thumbnail_url:
                thumbnail_url = thumbnail_url.replace("vi_webp", "vi").replace(".webp", ".jpg")

            return {
                "title": title,
                "thumbnail_url": thumbnail_url
            }

    except Exception as e:
        return {"error": str(e)}
    
@app.get("/read-file")
def read_file(file: str = Query(...)):
    try:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

@app.post("/generate-pdf")
async def generate_pdf(request: Request):
    try:
        data = await request.json()

        # 將 json 儲存成檔案
        os.makedirs("temp", exist_ok=True)
        with open("temp/merged_result.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 呼叫 PDF 生成程式
        result = subprocess.run(
            ["python3", "pdf_generattor.py"],
            cwd="/app", capture_output=True, text=True
        )

        if result.returncode != 0:
            return {"status": "fail", "error": result.stderr}

        return {"status": "success", "message": "PDF generated."}

    except Exception as e:
        return {"status": "fail", "error": str(e)}

