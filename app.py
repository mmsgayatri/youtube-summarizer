import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator  # You might need to install this package

# Configure your API key directly here
genai.configure(api_key="AIzaSyAcCjCbYvY3nk9cGTSTq4Odw5wHoJxfyHQ")

prompt = "Act as a YouTube video summarizer which will take the transcript of the video and provide the summary within 200 words and provide the summary of the text given."

# Function to get transcript data from YouTube videos in a specified language
def extract_transcript_details(youtube_video_url, language_code='en'):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript
    except Exception as e:
        raise e

# Function to translate text to a specified language
def translate_text(text, target_language='en'):
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

# Function to generate a summary using Gemini AI
def generate_gemini_content(transcript_text, prompt, target_language='en'):
    model = genai.GenerativeModel("gemini-pro")
    prompt_with_transcript = prompt + transcript_text
    response = model.generate_content(prompt_with_transcript, language=target_language)
    return response.text

st.title("YouTube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter your YouTube Link:")
source_language = st.text_input("Enter transcript language code (e.g., 'en', 'es'):", value='en')
target_language = st.text_input("Enter summary language code (e.g., 'en', 'es'):", value='en')

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    try:
        transcript_text = extract_transcript_details(youtube_link, source_language)
        if transcript_text:
            # Translate transcript to the target language
            translated_transcript = translate_text(transcript_text, target_language)
            # Generate summary in the target language
            summary = generate_gemini_content(translated_transcript, prompt, target_language)
            st.markdown("## Detailed Notes:")
            st.write(summary)
    except Exception as e:
        st.error(f"An error occurred: {e}")
