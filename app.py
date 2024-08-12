import re  # Ensure re module is imported
import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator

# Set your API key directly
genai.configure(api_key="AIzaSyAcCjCbYvY3nk9cGTSTq4Odw5wHoJxfyHQ")

# Regular expression to extract video code
def extract_video_code(youtube_url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, youtube_url)
    
    if match:
        return match.group(1)
    else:
        return None

# Getting the transcript data from YouTube videos
def extract_transcript_details(youtube_video_url, language='en'):
    try:
        video_id = extract_video_code(youtube_video_url)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript

    except Exception as e:
        raise e

# Generate summary based on the prompt 
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Translate summary into the desired language
def translate_summary(summary, target_language):
    translator = Translator()
    translation = translator.translate(summary, dest=target_language)
    return translation.text

# Define the prompt variable
prompt = "Act as a YouTube video summarizer which will take the transcript of the video and provide the summary within 200 words. Provide the summary of the text given."

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter your YouTube Link:")
target_language = st.text_input("Enter the language code for translation (e.g., 'es' for Spanish, 'fr' for French, etc.):", value='en')

if youtube_link:
    video_id = extract_video_code(youtube_link)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link, language=target_language)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        
        # If the user wants the summary in a different language
        if target_language and target_language != 'en':
            summary = translate_summary(summary, target_language)
        
        st.markdown("## Detailed Notes:")
        st.write(summary)
