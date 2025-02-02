import streamlit as st
import requests
import time
import os
import sys

# Ensure root project directory is in Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.config import RESULTS_DIR, LANGUAGE_CODES
from utils.validators import is_valid_google_drive_link


def translate_tab():
    """🌍 Video Translation Tab"""
    st.subheader("🌍 Translate Transcript")

    # 🔹 Input: Video URL
    drive_link = st.text_input(
        "🔗 **Google Drive Video Link**",
        key="translate_drive_link",
        placeholder="Paste your video link here...",
        help="Make sure your link is from Google Drive and shared publicly."
    )

    # 🔹 Select Target Language
    languages = list(LANGUAGE_CODES.keys())
    target_language = st.selectbox("🌍 **Select Target Language**", languages, index=1)

    # 🔹 Translate Button
    if st.button("🚀 Translate"):
        if not drive_link:
            st.warning("⚠️ Please enter a valid video link.")
        elif not is_valid_google_drive_link(drive_link):
            st.error("❌ Invalid Google Drive link. Please enter a correct Google Drive video link.")
        else:
            with st.status("⏳ Translating...", expanded=True) as status:
                steps = [
                    "📥 Extracting transcript with timestamps...",
                    f"🌍 Translating transcript to {target_language}...",
                    "📜 Generating translated transcript...",
                ]

                progress_bar = st.progress(0)

                for i, step in enumerate(steps):
                    st.write(step)
                    progress_bar.progress((i + 1) / len(steps))
                    time.sleep(2)  # Simulating processing time

                # 🔹 Send request to backend
                response = requests.post(
                    "http://127.0.0.1:5000/translate",
                    json={"video_url": drive_link, "target_language": LANGUAGE_CODES[target_language]}
                )

                if response.status_code == 200:
                    translation_data = response.json()
                    translated_text = translation_data.get("translated_text", "")
                    translated_file = translation_data.get("translated_file_path", "")

                    # ✅ Display Translated Text
                    status.update(label="✅ Translation Completed!", state="complete")
                    st.subheader("📜 Translated Transcript:")
                    st.text_area("📜 Translated Transcript", translated_text, height=300)

                    # 🔹 Provide a download button
                    if translated_file and os.path.exists(translated_file):
                        with open(translated_file, "r", encoding="utf-8") as file:
                            file_contents = file.read()
                        st.download_button(
                            label="📥 Download Translated Transcript",
                            data=file_contents,
                            file_name=f"translated_transcript_{LANGUAGE_CODES[target_language]}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ Translated transcript file not found!")

                else:
                    status.update(label="❌ Translation Failed!", state="error")
                    st.error("❌ Translation Failed: " + response.json().get("error", "Unknown error."))
