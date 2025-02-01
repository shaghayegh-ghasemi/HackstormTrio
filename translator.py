from deep_translator import GoogleTranslator

# Define the source and target languages
source_language = 'auto'  # Automatically detect the source language
target_language = 'fr'  # Target language (e.g., 'es' for Spanish)


# Function to translate and save the file
def translate_file(input_path, output_path):
    # Read the content from the source file
    with open(input_path, 'r', encoding='utf-8') as file:
        original_text = file.read()

    # Translate the text
    translated_text = GoogleTranslator(source=source_language, target=target_language).translate(original_text)

    # Write the translated text to a new file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(translated_text)

    print(f"Translation for {input_path} completed successfully.")


# Translate both files
translate_file('./results/transcript.txt', './results/transcript_translated.txt')
translate_file('./results/transcription.txt', './results/transcription_translated.txt')
