import re
import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from googletrans import Translator

# Configure Google API key
genai.configure(api_key="AIzaSyAcCjCbYvY3nk9cGTSTq4Odw5wHoJxfyHQ")

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
            return transcript.fetch()
    except NoTranscriptFound:
        return None
    except TranscriptsDisabled:
        # Transcripts are disabled for this video
        return None

# Extract and concatenate transcript text
def extract_transcript_details(youtube_video_url):
    video_id = extract_video_code(youtube_video_url)
    if not video_id:
        st.error("Invalid YouTube URL")
        return None

    # Attempt to fetch the transcript
    transcript = fetch_transcript(video_id)
    if transcript is not None:
        transcript_text = " ".join(item["text"] for item in transcript)
        return transcript_text

    st.error("No transcripts or subtitles available for this video.")
    return None

# Generate summary from transcript using Google Generative AI
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Translate summary into the desired language
def translate_summary(summary, target_language):
    translator = Translator()
    translation = translator.translate(summary, dest=target_language)
    return translation.text

# Define the prompt for summarization
prompt = "Act as a YouTube video summarizer which will take the transcript of the video and provide the summary within 200 words. Provide the summary of the text given."

# Streamlit app layout
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter your YouTube Link:")
target_language = st.text_input("Enter the language code for translation (e.g., 'es' for Spanish, 'fr' for French, etc.):", value='en')

if youtube_link:
    video_id = extract_video_code(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        
        if target_language and target_language != 'en':
            summary = translate_summary(summary, target_language)
        
        st.markdown("## Detailed Notes:")
        st.write(summary)
