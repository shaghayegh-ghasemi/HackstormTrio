import os
from moviepy import *
import whisper
from datetime import timedelta
import gdown
import pysrt
import cv2
import numpy as np
from deep_translator import GoogleTranslator
# Ensure the 'results' folder exists
os.makedirs('./results', exist_ok=True)
def download_video_from_gdrive(gdrive_url, output_path='./results/video.mp4'):
    """
    Downloads a video file from a Google Drive URL.
    """
    gdown.download(gdrive_url, output_path, quiet=False, fuzzy=True)
    return output_path
def extract_audio(video_path, audio_path='./results/audio.wav'):
    """
    Extracts audio from the video file and saves it as a WAV file.
    """
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')
    video.close()
    return audio_path
def transcribe_audio(audio_path, model_size='base'):
    """
    Transcribes the audio file using OpenAI's Whisper model.
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, verbose=True)
    return result
def translate_transcription(transcription, target_language='fr'):
    """
    Translates the transcription text into the target language.
    """
    translator = GoogleTranslator(source='auto', target=target_language)
    for segment in transcription['segments']:
        segment['text'] = translator.translate(segment['text'])
    return transcription
def generate_srt(transcription, srt_path='./results/subtitles.srt'):
    """
    Generates an SRT file from the transcription result.
    """
    def format_timestamp(seconds):
        td = timedelta(seconds=seconds)
        timestamp = str(td)
        if '.' in timestamp:
            timestamp = timestamp.replace('.', ',')[:12]
        else:
            timestamp += ',000'
        return timestamp
    srt_content = ""
    for i, segment in enumerate(transcription['segments']):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        text = segment['text'].strip()
        srt_content += f"{i + 1}\n{start} --> {end}\n{text}\n\n"
    with open(srt_path, 'w', encoding='utf-8') as srt_file:
        srt_file.write(srt_content)
    return srt_path
def overlay_subtitles(video_path, srt_path, output_path='./results/output_video.mp4'):
    """
    Overlays subtitles onto the video without a background box.
    """
    # Load video
    video = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    subs = pysrt.open(srt_path)
    font_scale = 1.5
    thickness = 3
    margin = 50
    max_width = frame_width - 100  # Leave some padding
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        current_time = video.get(cv2.CAP_PROP_POS_MSEC) / 1000
        for sub in subs:
            start_time = sub.start.seconds + sub.start.minutes * 60 + sub.start.hours * 3600
            end_time = sub.end.seconds + sub.end.minutes * 60 + sub.end.hours * 3600
            if start_time <= current_time <= end_time:
                text = sub.text
                words = text.split()
                lines = []
                line = ""
                # Break text into multiple lines if it exceeds max width
                for word in words:
                    test_line = line + " " + word if line else word
                    text_size = cv2.getTextSize(test_line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
                    if text_size[0] > max_width:
                        lines.append(line)
                        line = word
                    else:
                        line = test_line
                lines.append(line)
                text_height = (cv2.getTextSize("A", cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0][1] + 10) * len(lines)
                position = (50, frame_height - text_height - margin)
                # Draw text lines without a background box
                y_offset = position[1]
                for line in lines:
                    cv2.putText(frame, line, (position[0], y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                                (255, 255, 255), thickness, cv2.LINE_AA)
                    y_offset += cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0][1] + 10
        out.write(frame)
    video.release()
    out.release()
    # Merge original audio with the new video
    final_output = './results/final_output.mp4'
    video_clip = VideoFileClip(output_path)
    original_audio = VideoFileClip(video_path).audio
    video_clip = video_clip.with_audio(original_audio)
    video_clip.write_videofile(final_output, codec='libx264', audio_codec='aac')
    return final_output
def main(gdrive_url):
    """
    Main function to process the video: download, transcribe, translate, generate subtitles, overlay them, and ensure audio is retained.
    """
    video_path = download_video_from_gdrive(gdrive_url)
    audio_path = extract_audio(video_path)
    transcription = transcribe_audio(audio_path)
    translated_transcription = translate_transcription(transcription, 'fr')
    srt_path = generate_srt(translated_transcription)
    final_video = overlay_subtitles(video_path, srt_path)
    print(f"Final video saved as: {final_video}")
if __name__ == "__main__":
    gdrive_url = "https://drive.google.com/file/d/1x2HlTWOH2_rJJWeEU7xl5na-mtfCqKV2/view?usp=drive_link"
    main(gdrive_url)

