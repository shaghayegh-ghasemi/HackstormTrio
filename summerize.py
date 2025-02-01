import os
import requests
from moviepy import *
import whisper

def seconds_to_hms(seconds):
    """
    Converts seconds into hours, minutes, and seconds (hh:mm:ss).
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def get_google_drive_url(file_id):
    """
    Generates the direct download URL for a Google Drive file.
    """
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def download_video(url, output_path):
    """
    Downloads a video from a URL to the specified output path.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Video downloaded successfully: {output_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {e}")


def extract_audio_from_video(video_path, audio_path):
    """
    Extracts audio from a video file and saves it as an audio file.
    """
    try:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        print(f"Audio extracted successfully: {audio_path}")
    except Exception as e:
        print(f"Error extracting audio: {e}")


def transcribe_audio(audio_path, model_size="base"):
    """
    Transcribes audio to text using OpenAI's Whisper model.
    """
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path)
        return result
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def save_transcription(transcription_result, transcript_path):
    """
    Saves the transcription result with timestamps to a text file.
    """
    try:
        with open(transcript_path, 'w') as f:
            for segment in transcription_result['segments']:
                start_time = segment['start']
                text = segment['text']
                time_str = seconds_to_hms(start_time)  # Convert to hh:mm:ss
                f.write(f"At {time_str}: {text}\n")
        print(f"Transcription saved successfully: {transcript_path}")
    except Exception as e:
        print(f"Error saving transcription: {e}")


def main(video_url):
    # Ensure the results directory exists
    os.makedirs('./results', exist_ok=True)

    # Define paths
    video_path = "./results/downloaded_video.mp4"
    audio_path = "./results/extracted_audio.wav"
    transcript_path = "./results/transcription.txt"

    # Extract file ID from Google Drive URL
    file_id = video_url.split('/d/')[1].split('/')[0]
    direct_url = get_google_drive_url(file_id)

    # Download the video from the URL
    download_video(direct_url, video_path)

    # Extract audio from the downloaded video
    extract_audio_from_video(video_path, audio_path)

    # Transcribe the audio to text
    transcription_result = transcribe_audio(audio_path)

    if transcription_result:
        # Save the transcription with timestamps
        save_transcription(transcription_result, transcript_path)
    else:
        print("Transcription failed.")


if __name__ == "__main__":
    # Replace with your actual Google Drive video URL
    video_url = "https://drive.google.com/file/d/1x2HlTWOH2_rJJWeEU7xl5na-mtfCqKV2/view?usp=drive_link"
    main(video_url)
