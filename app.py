import re
import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator

def extract_video_code(youtube_url):
    # Regular expression pattern to match the video code
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, youtube_url)
    
    if match:
        return match.group(1)
    else:
        return None

# Configure the Google API key
genai.configure(api_key="AIzaSyAcCjCbYvY3nk9cGTSTq4Odw5wHoJxfyHQ")
prompt = "Act as a YouTube video summarizer. Take the transcript of the video and provide a summary within 200 words in "

## Getting the transcript data from YouTube videos
def extract_transcript_details(youtube_video_url, target_language):
    try:
        video_id = extract_video_code(youtube_video_url)
        
        # Retrieve the available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Initialize variables to store the transcript details
        transcript_text = ""
        transcript_language = target_language
        
        # Iterate over all available transcripts to find the most suitable one
        for transcript in transcript_list:
            print(
                transcript.video_id,
                transcript.language,
                transcript.language_code,
                transcript.is_generated,
                transcript.is_translatable,
                transcript.translation_languages,
            )
            
            # Fetch the actual transcript data
            transcript_data = transcript.fetch()
            
            # Translate the transcript to the target language if necessary
            if transcript.language_code != target_language and transcript.is_translatable:
                transcript = transcript.translate(target_language)
                transcript_language = transcript.language_code
            
            # Combine the transcript text
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
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

# Streamlit app UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter your YouTube Link:")
target_language = st.text_input("Enter the target language code (e.g., 'en' for English, 'es' for Spanish):", value="en")

if youtube_link and target_language:
    video_id = extract_video_code(youtube_link)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

    if st.button("Get Detailed Notes"):
        transcript_text, transcript_language = extract_transcript_details(youtube_link, target_language)

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            if target_language != 'en':  # Only translate if the target language is not English
                summary = translate_text(summary, target_language)
            st.markdown("## Detailed Notes:")
            st.write(f"**Language:** {target_language}")
            st.write(summary)
