import os
import datetime
from langchain.prompts.prompt import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import sys

# 🔹 Ensure Python can find `utils/`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.config import RESULTS_DIR  # ✅ Import shared directory

# Load environment variables
load_dotenv()

# Summary Template
summary_template = """
Given the video transcript {information}, provide:
1. A short summary.
"""

summary_prompt_template = PromptTemplate(
    input_variables=["information"], template=summary_template
)

llm = ChatOllama(model="llama3")

def summarize_text(video_transcript, save=True):
    """
    Generate a summary from a video transcript.
    If `save=True`, the summary is saved to a file.
    Returns the summary text and the file path if saved.
    """
    chain = summary_prompt_template | llm | StrOutputParser()
    result = chain.invoke(input={"information": video_transcript})

    file_path = None  # Default: No file saved
    if save:
        file_path = save_summary(result)

    return result, file_path  # ✅ Return both summary text and file path

def save_summary(summary_text, filename=None):
    """
    Save the summarized text to a file in the shared `results/` directory.
    """
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.txt"

    summary_path = os.path.join(RESULTS_DIR, filename)
    
    try:
        with open(summary_path, "w") as f:
            f.write(summary_text)
        print(f"✅ Summary saved: {summary_path}")
        return summary_path  # ✅ Return file path
    except Exception as e:
        print(f"❌ Error saving summary: {e}")
        return None
