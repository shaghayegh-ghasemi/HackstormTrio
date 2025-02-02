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
    st.subheader("🌍 Translate Transcript & Subtitles")

    # 🔹 Input: Video URL
    drive_link = st.text_input("🔗 **Google Drive Video Link**", key="translate_drive_link",
                               placeholder="Paste your video link here...",
                               help="Make sure your link is from Google Drive and shared publicly.")

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
                st.write("📥 Extracting transcript with timestamps...")
                st.write(f"🌍 Translating to {target_language}...")

                # 🔹 Send request to backend
                response = requests.post(
                    "http://127.0.0.1:5000/translate",
                    json={"video_url": drive_link, "target_language": LANGUAGE_CODES[target_language]}
                )

                if response.status_code == 200:
                    translation_data = response.json()
                    transcript_file = translation_data.get("translated_transcript", "")
                    download_url = translation_data.get("download_url", "")

                    status.update(label="✅ Translation Completed!", state="complete")
                    st.text_area("📜 Translated Transcript", open(transcript_file, "r").read(), height=200)

                    # 🔹 Provide a download button
                    if transcript_file and os.path.exists(transcript_file):
                        with open(transcript_file, "r") as file:
                            file_contents = file.read()
                        st.download_button(
                            label="📥 Download Translated Transcript",
                            data=file_contents,
                            file_name=f"translated_transcript_{LANGUAGE_CODES[target_language]}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ Translated transcript file not found!")

                    # # 🔹 Display backend download link (Optional)
                    # if download_url:
                    #     st.markdown(f"[📥 Download from Backend]({download_url})", unsafe_allow_html=True)

                else:
                    status.update(label="❌ Translation Failed!", state="error")
                    st.error("❌ Translation Failed: " + response.json().get("error", "Unknown error."))
