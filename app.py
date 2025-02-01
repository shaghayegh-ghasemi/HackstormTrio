import streamlit as st
import requests
from flask import Flask, request, jsonify
import threading
import time
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

# page title
st.set_page_config(page_title="Hackstorm Trio", page_icon="⚡")

# Streamlit UI
st.title("🎥 Video Summarizer")

st.write("🚀 Welcome to **Hackstorm Trio**'s AI-powered Video Summarization Tool!")

st.write("Enter a Google Drive video link to generate a summary.")

# User Input
drive_link = st.text_input("🔗 Google Drive Video Link")

if st.button("🚀 Generate Summary"):
    if drive_link:
        with st.status("⏳ Processing your video...", expanded=True) as status:
            steps = [
                "📥 Downloading video from Google Drive...",
                "🎵 Extracting audio...",
                "📝 Transcribing audio...",
                "🤖 Generating summary with AI..."
            ]

            progress_bar = st.progress(0)

            for i, step in enumerate(steps):
                st.write(step)  # Display step progress
                progress_bar.progress((i + 1) / len(steps))  # Update progress
                time.sleep(2)  # Simulate processing time

            response = requests.post(
                "http://127.0.0.1:5000/summarize",
                json={"drive_link": drive_link}
            )

            if response.status_code == 200:
                summary = response.json().get("summary", "No summary generated.")
                status.update(label="✅ Summary Ready!", state="complete")
                st.subheader("📜 Summary:")
                st.write(summary)
            else:
                status.update(label="❌ Error!", state="error")
                st.error("Error: " + response.json().get("error", "Unknown error."))
    else:
        st.warning("⚠️ Please enter a valid video link.")
