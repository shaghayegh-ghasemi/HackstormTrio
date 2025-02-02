import os
from moviepy import *
import whisper
from datetime import timedelta
import gdown
import pysrt
import cv2
import numpy as np
from deep_translator import GoogleTranslator
from PIL import Image, ImageDraw, ImageFont
# Ensure the 'results' folder exists
os.makedirs('./results', exist_ok=True)
def download_video_from_gdrive(gdrive_url, output_path='./results/video.mp4'):
    gdown.download(gdrive_url, output_path, quiet=False, fuzzy=True)
    return output_path
def extract_audio(video_path, audio_path='./results/audio.wav'):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')
    video.close()
    return audio_path
def transcribe_audio(audio_path, model_size='base'):
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, verbose=True)
    return result
def translate_text(text, target_language='fr'):
    translator = GoogleTranslator(source='auto', target=target_language)
    return translator.translate(text)
def translate_transcription(transcription, target_language='fr'):
    for segment in transcription['segments']:
        segment['text'] = translate_text(segment['text'], target_language)
    return transcription
def generate_srt(transcription, srt_path='./results/subtitles.srt'):
    def format_timestamp(seconds):
        td = timedelta(seconds=seconds)
        timestamp = str(td).replace('.', ',')[:12] if '.' in str(td) else str(td) + ',000'
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
    video = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    subs = pysrt.open(srt_path)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 40)
    max_width = frame_width - 100
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(frame_pil)
        current_time = video.get(cv2.CAP_PROP_POS_MSEC) / 1000
        for sub in subs:
            start_time = sub.start.ordinal / 1000.0
            end_time = sub.end.ordinal / 1000.0
            if start_time <= current_time <= end_time:
                text = sub.text
                words = text.split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    text_width = bbox[2] - bbox[0]
                    if text_width > max_width:
                        lines.append(current_line)
                        current_line = word
                    else:
                        current_line = test_line
                lines.append(current_line)
                text_height = (bbox[3] - bbox[1] + 10) * len(lines)
                position = (50, frame_height - text_height - 50)
                y_offset = position[1]
                for line in lines:
                    draw.text((position[0], y_offset), line, font=font, fill=(255, 255, 255))
                    y_offset += bbox[3] - bbox[1] + 10
        frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
        out.write(frame)
    video.release()
    out.release()
    final_output = './results/final_video_with_subtitles.mp4'
    video_clip = VideoFileClip(output_path)
    original_audio = VideoFileClip(video_path).audio
    final_video = video_clip.with_audio(original_audio)
    final_video.write_videofile(final_output, codec='libx264', audio_codec='aac')
    return final_output
def main(gdrive_url):
    video_path = download_video_from_gdrive(gdrive_url)
    audio_path = extract_audio(video_path)
    transcription = transcribe_audio(audio_path)
    translated_transcription = translate_transcription(transcription, 'fr')
    srt_path = generate_srt(translated_transcription)
    final_video = overlay_subtitles(video_path, srt_path)
    print(f"Final translated video with subtitles saved as: {final_video}")
if __name__ == "__main__":
    gdrive_url = "https://drive.google.com/file/d/1x2HlTWOH2_rJJWeEU7xl5na-mtfCqKV2/view?usp=drive_link"
    main(gdrive_url)