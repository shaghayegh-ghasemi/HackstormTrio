import streamlit as st
import requests
from flask import Flask, request, jsonify
import threading
import time
from utils.drive_utils import transcript
from utils.summarization import summarize_text

# Set Page Configuration
st.set_page_config(
    page_title="Hackstorm Trio",
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

# Centered layout with optimal whitespace
left_space, content, right_space = st.columns([1, 3, 1])  # Adjusted to make content wider

with content:  # Content will take 3/5 of the page width
    st.markdown("<h2 style='text-align: center;'>⚡ Welcome to Hackstorm Trio's AI-powered Video Summarization Tool! ⚡</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>🎥 Video Summarizer</h3>", unsafe_allow_html=True)
    st.write("Enter a **Google Drive video link** below, and our AI will generate a concise summary for you.")

    # 🔹 Input Field Styling 🔹
    st.markdown(
        """
        <style>
        .small-input input {
            width: 50% !important;  /* Adjust width (balanced) */
            margin: 0 auto !important; /* Center the input field */
            display: flex !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    drive_link = st.text_input(
        "🔗 **Google Drive Video Link**",
        key="drive_link",
        placeholder="Paste your video link here...",
        help="Make sure your link is from Google Drive and shared publicly.",
    )

    # Reduce input width
    st.markdown('<div class="small-input"></div>', unsafe_allow_html=True)

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
            "image": "https://raw.githubusercontent.com/shaghayegh-ghasemi/HackstormTrio/refs/heads/shaghayegh/assets/contributors/shaghayegh.JPG?token=GHSAT0AAAAAAC5C7XVIIMAY526TLFTMDEZSZ46RUGA",
            "github": "https://github.com/shaghayegh-ghasemi"
        },
        {
            "name": "Milad Khanchi",
            "image": "https://raw.githubusercontent.com/shaghayegh-ghasemi/HackstormTrio/refs/heads/shaghayegh/assets/contributors/milad.JPG?token=GHSAT0AAAAAAC5C7XVI53JRDNK67QKKAI3GZ46RYYA",
            "github": "https://github.com/Milad-Khanchi"
        },
        {
            "name": "Qian Sun",
            "image": "https://raw.githubusercontent.com/shaghayegh-ghasemi/HackstormTrio/refs/heads/shaghayegh/assets/contributors/qian.jpg?token=GHSAT0AAAAAAC5C7XVJMBCS6DAI3RAJW43AZ46RX2Q",
            "github": "https://github.com/chin-sun"
        }
    ]

    # Custom CSS for Centering Name & GitHub Link
    st.markdown(
        """
        <style>
        .profile-container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            text-align: center;
        }
        .profile-pic {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #ddd;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
        .profile-text {
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
        }
        .profile-link {
            text-align: center;
            font-size: 14px;
            color: #007BFF;
            text-decoration: none;
            font-weight: bold;
        }
        .profile-link:hover {
            text-decoration: underline;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Centered Layout for Contributors
    cols = st.columns(3)

    for i, contributor in enumerate(contributors):
        with cols[i]:
            st.markdown(
                f"""
                <div class="profile-container">
                    <img src="{contributor['image']}" class="profile-pic">
                    <p class="profile-text">{contributor['name']}</p>
                    <a href="{contributor['github']}" class="profile-link">🔗 GitHub Profile</a>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Footer Branding
    st.markdown("---")
    st.markdown("🔹 **Hackstorm Trio** - AI-Powered Innovation 🚀")
    st.markdown("💡 Developed with ❤️ by Hackstorm Trio")
