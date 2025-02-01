import streamlit as st
import requests
from flask import Flask, request, jsonify
import threading
from utils.drive_utils import transcript
from utils.summarization import summarize_text

# Flask Backend
app = Flask(__name__)

@app.route('/summarize', methods=['POST'])
def summarize():
    """Handles summarization requests."""
    try:
        data = request.json
        drive_link = data.get("drive_link")

        if not drive_link:
            return jsonify({"error": "No video URL provided"}), 400

        # Get transcript
        video_text = transcript(drive_link)

        # Generate summary
        summary = summarize_text(video_text)

        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask in a separate thread
def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)

threading.Thread(target=run_flask, daemon=True).start()

# Streamlit UI
st.title("🎥 Video Summarizer")
st.write("Enter a Google Drive video link to generate a summary.")

# User Input
drive_link = st.text_input("Google Drive Video Link")

if st.button("Generate Summary"):
    if drive_link:
        st.write("Processing...")

        response = requests.post(
            "http://127.0.0.1:5000/summarize",
            json={"drive_link": drive_link}
        )

        if response.status_code == 200:
            summary = response.json().get("summary", "No summary generated.")
            st.subheader("Summary:")
            st.write(summary)
        else:
            st.error("Error: " + response.json().get("error", "Unknown error."))
    else:
        st.warning("Please enter a valid video link.")
