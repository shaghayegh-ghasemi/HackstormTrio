import streamlit as st
import os
import sys
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.validators import is_valid_google_drive_link  # ✅ Import validation function
from utils.config import LANGUAGE_CODES

def subtitle_tab():
    """🔠 Subtitle Generation Tab"""
    st.subheader("🔠 Generate Subtitles")
    st.write("Enter a video URL and choose a target language to generate subtitles.")

    # 🔹 Input: Video URL (same as other tabs)
    drive_link = st.text_input("🔗 **Google Drive Video Link**", key="subtitle_drive_link",
                               placeholder="Paste your video link here...",
                               help="Make sure your link is from Google Drive and shared publicly.")

    # 🔹 Input: Target Language Selection
    languages = list(LANGUAGE_CODES.keys())
    target_language = st.selectbox("🌍 **Select Target Language for Subtitles**", languages, index=0)

    # 🔹 Handle Custom Language Input
    language_code = LANGUAGE_CODES[target_language]  # Get predefined language code
 
    # 🔹 Generate Subtitles Button
    if st.button("🚀 Generate Subtitles"):
        if not drive_link:
            st.warning("⚠️ Please enter a valid video link.")
        elif not is_valid_google_drive_link(drive_link):
            st.error("❌ Invalid Google Drive link. Please enter a correct Google Drive video link.")
        elif not language_code:
            st.error("❌ Please enter a valid language code.")
        else:
            with st.status("⏳ Processing your video...", expanded=True):
                st.write("📥 Downloading video...")
                st.write("🎵 Extracting audio...")
                st.write(f"📝 Generating subtitles in {target_language} ({language_code})...")

                # 🔹 Send request to backend for subtitle generation
                response = requests.post(
                    "http://127.0.0.1:5000/generate_subtitles",
                    json={"video_url": drive_link, "target_language": language_code},
                    timeout=300
                )

                if response.status_code == 200:
                    subtitle_data = response.json()
                    subtitle_path = subtitle_data.get("subtitle_file")
                    final_video = subtitle_data.get("final_video")

                    st.success("✅ Subtitles generated successfully!")

                    # 🔹 Provide download buttons for subtitles and final video
                    if subtitle_path and os.path.exists(subtitle_path):
                        with open(subtitle_path, "r") as file:
                            file_contents = file.read()
                        st.download_button(
                            label="📥 Download Subtitles (SRT)",
                            data=file_contents,
                            file_name="subtitles.srt",
                            mime="text/plain"
                        )

                    if final_video and os.path.exists(final_video):
                        with open(final_video, "rb") as file:
                            st.download_button(
                                label="🎬 Download Final Video",
                                data=file,
                                file_name="final_video_with_subtitles.mp4",
                                mime="video/mp4"
                            )
                else:
                    st.error(f"❌ Error: {response.json().get('error', 'Unknown error')}")