import sys
import os

# 🔹 Ensure Python can find `utils/`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.transcript import transcript_with_timeline, transcript
from utils.summarization import summarize_text
from utils.config import RESULTS_DIR
from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# --- API 1: Extract Transcript from Video with timeline ---
@app.route('/transcript', methods=['POST'])
def get_transcript():
    """Extract transcript from uploaded video."""
    try:
        data = request.json
        video_url = data.get("video_url")
        use_timeline = data.get("use_timeline", False)  # Default to False

        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400

        if use_timeline:
            transcript_path = transcript_with_timeline(video_url)  # Generate timeline transcript
            if transcript_path and os.path.exists(transcript_path):
                with open(transcript_path, "r") as file:
                    timeline_transcript = file.read()
                return jsonify({"transcript": timeline_transcript, "file_path": transcript_path})  # ✅ Correct path
            return jsonify({"error": "Failed to generate transcript with timestamps"}), 500
        else:
            plain_transcript = transcript(video_url)  # Generate plain transcript
            if plain_transcript:
                return jsonify({"transcript": plain_transcript})
            return jsonify({"error": "Failed to generate transcript"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- API 2: Summarization (Basic) ---
@app.route('/summarize', methods=['POST'])
def get_summary():
    """Generate AI-powered video summary and return file path for download"""
    try:
        data = request.json
        transcript_text = data.get("transcript")

        if not transcript_text:
            return jsonify({"error": "No transcript provided"}), 400

        # ✅ Now correctly handles both summary and file path
        summary, file_path = summarize_text(transcript_text, save=True)

        return jsonify({"summary": summary, "file_path": file_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# --- API 4: Translate Summary ---
# @app.route('/translate', methods=['POST'])
# def translate_summary():
#     """Translate summary into different languages"""
#     data = request.json
#     summary_text = data.get("summary")
#     language = data.get("language")

#     if not summary_text or not language:
#         return jsonify({"error": "Missing summary or target language"}), 400

#     translated_text = translate_text(summary_text, language)
#     return jsonify({"translated_summary": translated_text})


# --- API 5: Generate Subtitles ---
# @app.route('/subtitles', methods=['POST'])
# def generate_video_subtitles():
#     """Generate subtitles for a video"""
#     data = request.json
#     video_url = data.get("video_url")

#     if not video_url:
#         return jsonify({"error": "No video URL provided"}), 400

#     subtitle_file = generate_subtitles(video_url)
#     return jsonify({"subtitles": subtitle_file})


# 

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5000, threads=4)