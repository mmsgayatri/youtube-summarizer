import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator
import re

# Function to extract video code from YouTube URL
def extract_video_code(youtube_url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, youtube_url)
    
    if match:
        return match.group(1)
    else:
        return None

# Configure the Google API key directly
genai.configure(api_key="AIzaSyAcCjCbYvY3nk9cGTSTq4Odw5wHoJxfyHQ")
prompt = "Act as a YouTube video summarizer. Take the transcript of the video and provide a summary within 200 words in "

# Function to get transcript data from YouTube videos
def extract_transcript_details(youtube_video_url, target_language):
    try:
        video_id = extract_video_code(youtube_video_url)
        
        # Retrieve the available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        transcript_text = ""
        transcript_language = target_language
        
        for transcript in transcript_list:
            transcript_data = transcript.fetch()
            
            if transcript.language_code != 'en' and transcript.is_translatable:
                transcript = transcript.translate('en')  # Always translate to English for summarization
                transcript_language = transcript.language_code
            
            for i in transcript_data:
                transcript_text += " " + i["text"]
            
            break  # Use the first suitable transcript found
        
        return transcript_text, transcript_language

    except Exception as e:
        raise e

# Generate summary based on the prompt
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Translate text to the target language
def translate_text(text, target_language):
    if target_language != 'en':  # Only translate if the target language is not English
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        return translated.text
    return text

# Streamlit app UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter your YouTube Link:")
target_language = st.text_input("Enter the target language code (e.g., 'en' for English, 'es' for Spanish):", value="en")

if youtube_link and target_language:
    video_id = extract_video_code(youtube_link)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

    if st.button("Get Detailed Notes"):
        transcript_text, transcript_language = extract_transcript_details(youtube_link, 'en')

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            summary = translate_text(summary, target_language)
            st.markdown("## Detailed Notes:")
            st.write(f"**Language:** {target_language}")
            st.write(summary)
