import os
from deep_translator import GoogleTranslator
from utils.config import RESULTS_DIR  # ✅ Import shared results directory
from utils.transcript import transcript_with_timeline  # ✅ Import function to extract transcript with timestamps

# Ensure 'results' directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)


### **🔹 Function: Translate a Given File**
def translate_file(input_filename, output_filename, target_language="fr"):
    """
    Translate a text file and save the translated version.
    
    Parameters:
        input_filename (str): The name of the file to translate.
        output_filename (str): The output filename for the translated text.
        target_language (str): Target language (default is French "fr").
    
    Returns:
        str: Path to the translated file.
    """
    input_path = os.path.join(RESULTS_DIR, input_filename)
    output_path = os.path.join(RESULTS_DIR, output_filename)

    # Ensure the input file exists
    if not os.path.exists(input_path):
        print(f"❌ Error: {input_path} not found!")
        return None

    # Read the content from the source file
    with open(input_path, "r", encoding="utf-8") as file:
        original_text = file.read()

    # Translate the text
    translated_text = GoogleTranslator(source="auto", target=target_language).translate(original_text)

    # Write the translated text to a new file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(translated_text)

    print(f"✅ Translation completed: {output_path}")
    return output_path


### **🔹 Function: Extract and Translate Transcript with Timeline**
def extract_and_translate_transcript(video_url, target_language="fr"):
    """
    1️⃣ Extracts the transcript with timeline from the video.
    2️⃣ Translates it into the target language.
    
    Parameters:
        video_url (str): Google Drive video link
        target_language (str): Target language code (e.g., "fr" for French)
    
    Returns:
        dict: Paths to the original and translated transcripts
    """
    print("📥 Extracting transcript with timeline...")
    transcript_path = transcript_with_timeline(video_url)

    if not transcript_path:
        print("❌ Failed to extract transcript.")
        return {"error": "Transcript extraction failed"}

    print(f"✅ Transcript extracted: {transcript_path}")

    # Define translated file name
    translated_filename = f"transcript_with_timeline_{target_language}.txt"

    print(f"🌍 Translating transcript to {target_language}...")
    translated_transcript_path = translate_file(
        os.path.basename(transcript_path), translated_filename, target_language
    )

    return {
        "original_transcript": transcript_path,
        "translated_transcript": translated_transcript_path
    }
