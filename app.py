import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator

# Configure the Google API key directly
genai.configure(api_key="AIzaSyAcCjCbYvY3nk9cGTSTq4Odw5wHoJxfyHQ")  # Replace with your actual API key
prompt = "Act as a YouTube video summarizer. Take the transcript of the video and provide a summary within 200 words in "

# Get transcript details from YouTube videos
def extract_transcript_details(youtube_video_url, target_language):
    try:
        video_id = youtube_video_url.split("=")[1]
        
        # Retrieve the available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Initialize variables to store transcript details
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
        st.error(f"Error fetching transcript: {e}")
        return None, None

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
    video_id = youtube_link.split("=")[1]
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
