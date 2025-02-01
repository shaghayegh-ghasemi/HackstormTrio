import streamlit as st
import requests
from flask import Flask, request, jsonify
import threading
import time
from utils.drive_utils import transcript
from utils.summarization import summarize_text

# Set Page Configuration
st.set_page_config(
    page_title="Hackstorm Trio - Video Summarizer",
    page_icon="⚡",
    layout="wide"
)

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

# Streamlit UI - Hackstorm Trio Branding
st.title("🎥 Video Summarizer")
st.markdown("<h4 style='text-align: center;'>🚀 Welcome to Hackstorm Trio's AI-powered Video Summarization Tool!</h4>", unsafe_allow_html=True)
st.write("Enter a **Google Drive video link** below, and our AI will generate a concise summary for you.")

# User Input
drive_link = st.text_input("🔗 **Google Drive Video Link**")

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

# --- 📌 Contributors Section ---
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>👨‍💻 Hackstorm Trio Contributors 🚀</h2>", unsafe_allow_html=True)

# Contributor details (Replace with actual image URLs and GitHub links)
contributors = [
    {
        "name": "Shaghayegh Ghasemi",
        "image": "https://avatars.githubusercontent.com/u/1?v=4",  # Replace with actual image
        "github": "https://github.com/shaghayegh-ghasemi"
    },
    {
        "name": "Milad Khanchi",
        "image": "https://avatars.githubusercontent.com/u/2?v=4",  # Replace with actual image
        "github": "https://github.com/Milad-Khanchi"
    },
    {
        "name": "Qian Sun",
        "image": "https://avatars.githubusercontent.com/u/3?v=4",  # Replace with actual image
        "github": "https://github.com/chin-sun"
    }
]

# Centered Layout for Contributors
cols = st.columns(3)

for i, contributor in enumerate(contributors):
    with cols[i]:
        st.image(contributor["image"], width=150, use_column_width=False)
        st.markdown(f"### [{contributor['name']}]({contributor['github']})")
        st.markdown("[🔗 GitHub Profile](" + contributor["github"] + ")")

# Footer Branding
st.markdown("---")
st.markdown("🔹 **Hackstorm Trio** - AI-Powered Innovation 🚀")
st.markdown("💡 Developed with ❤️ by Hackstorm Trio")