import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
from googletrans import Translator
import time

# Load environment variables
load_dotenv()

# Configure the Google API key
genai.configure(api_key=os.getenv("AIzaSyAcCjCbYvY3nk9cGTSTq4Odw5wHoJxfyHQ"))

# Define the prompt for summarization
prompt = "Act as a YouTube video summarizer. Take the transcript of the video and provide a summary within 200 words."

# Extract video code from YouTube URL
def extract_video_code(youtube_url):
  pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'  # Removed the non-breaking space character
  match = re.search(pattern, youtube_url)
  return match.group(1) if match else None

# Fetch transcript or subtitles in any available language
def fetch_transcript(video_id):
  try:
    transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    for transcript in transcripts:
      return transcript.fetch(), transcript.language_code
  except (NoTranscriptFound, TranscriptsDisabled):
    return None, None

# Retry decorator
def retry(func, retries=3, delay=2):
  for i in range(retries):
    try:
      return func()
    except Exception as e:
      if i < retries - 1:
        time.sleep(delay)  # Wait before retrying
      else:
        raise e

# Extract and concatenate transcript text
def extract_transcript_details(youtube_video_url, target_language):
  video_id = extract_video_code(youtube_video_url)
  if not video_id:
    st.error("Invalid YouTube URL")
    return None, None

  try:
    transcript_data, transcript_language = retry(lambda: fetch_transcript(video_id))
    if transcript_data:
      transcript_text = " ".join(item["text"] for item in transcript_data)
      if target_language and target_language != 'en':
        translator = Translator()
        transcript_text = retry(lambda: translator.translate(transcript_text, dest=target_language).text)
      return transcript_text, transcript_language
    else:
      st.error("No transcripts or subtitles available for this video.")
      return None, None
  except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    return None, None

# Generate summary from transcript using Google Generative AI
def generate_gemini_content(transcript_text, prompt):
  try:
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text
  except Exception as e:
    st.error(f"Failed to generate summary: {str(e)}")
    return None

# Translate text to the target language
def translate_text(text, target_language):
  if target_language == 'en':
    return text  # No translation needed if target language is English
  try:
    translator = Translator()
    translated = retry(lambda: translator.translate(text, dest=target_language).text)
    return translated
  except Exception as e:
    st.error(f"Failed to translate text: {str(e)}")
    return text

# Streamlit app UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter your YouTube Link:")
target_language = st.text_input("Enter the target language code (e.g., 'en' for English, 'es' for Spanish):", value="en")

if youtube_link and target_language:
  video_id = extract_video_code(youtube_link)
  if video_id:
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=
