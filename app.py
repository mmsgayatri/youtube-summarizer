import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator

# Load environment variables
load_dotenv()

# Configure the Google API key
genai.configure(api_key=os.getenv("AIzaSyAcCjCbYvY3nk9cGTSTq4Odw5wHoJxfyHQ"))

# Define the prompt for summarization
prompt = "Act as a YouTube video summarizer. Take the transcript of the video and provide a summary within 200 words."

# Extract video code from YouTube URL
def extract_video_code(youtube_url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, youtube_url)
    return match.group(1) if match else None

# Fetch transcript or subtitles in any available language
def fetch_transcript(video_id):
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        # Fetch the first available transcript
        for transcript in transcripts:
            transcript_data = transcript.fetch()
            return transcript_data, transcript.language_code
    except (NoTranscriptFound, TranscriptsDisabled):
        return None, None

# Extract and concatenate transcript text
def extract_transcript_details(youtube_video_url, target_language):
    video_id = extract_video_code(youtube_video_url)
    if not video_id:
        st.error("Invalid YouTube URL")
        return None, None

    # Attempt to fetch the transcript
    transcript_data, transcript_language = fetch_transcript(video_id)
    if transcript_data:
        transcript_text = " ".join(item["text"] for item in transcript_data)
        # Translate the transcript to the target language if necessary
        if target_language and target_language != 'en':
            translator = Translator()
            transcript_text = translator.translate(transcript_text, dest=target_language).text
        return transcript_text, transcript_language

    st.error("No transcripts or subtitles available for this video.")
    return None, None

# Generate summary from transcript using Google Generative AI
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Translate text to the target language
def translate_text(text, target_language):
    if target_language == 'en':
        return text  # No translation needed if target language is English
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

# Streamlit app UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter your YouTube Link:")
target_language = st.text_input("Enter the target language code (e.g., 'en' for English, 'es' for Spanish):", value="en")

if youtube_link and target_language:
    video_id = extract_video_code(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

    if st.button("Get Detailed Notes"):
        transcript_text, transcript_language = extract_transcript_details(youtube_link, target_language)

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            summary = translate_text(summary, target_language)
            st.markdown("## Detailed Notes:")
            st.write(f"**Language:** {target_language}")
            st.write(summary)
