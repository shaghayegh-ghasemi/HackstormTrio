import gdown
import os
import whisper
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

os.environ["PATH"] += os.pathsep + "C:/ffmpeg/bin"

def download_video(drive_link, output_path="video.mp4"):
    """Download video from Google Drive given its shareable link."""
    file_id = drive_link.split("/d/")[1].split("/")[0]  # Extract file ID
    gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=False)
    return output_path

def extract_audio(video_path, audio_path="audio.wav"):
    """Extract audio from a video file."""
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    return audio_path

def transcribe_audio(audio_path):
    """Convert audio to text using Whisper AI."""
    model = whisper.load_model("tiny")  # base _ Change to "tiny" for faster but less accurate transcription
    result = model.transcribe(audio_path)
    return result["text"]

# 🔹 Provide Google Drive link
drive_link = "https://drive.google.com/file/d/1x2HlTWOH2_rJJWeEU7xl5na-mtfCqKV2/view?usp=drive_link"

# 🔹 Get transcript
video_path = download_video(drive_link)
audio_path = extract_audio(video_path)
transcript = transcribe_audio(audio_path)

# 🔹 Print transcript
print("\n🔹 Transcript:\n", transcript)

# 🔹 Save transcript
with open("transcript.txt", "w") as f:
    f.write(transcript)
