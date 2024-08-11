import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
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

# Configure the Google API key directly (replace 'YOUR_GOOGLE_API_KEY' with your actual API key)
genai.configure(api_key="AIzaSyAcCjCbYvY3nk9cGTSTq4Odw5wHoJxfyHQ")
prompt_template = "Act as a YouTube video summarizer. Take the transcript of the video and provide a summary within 200 words in {}: "

# Function to get transcript data from YouTube videos
def extract_transcript_details(youtube_video_url, target_language):
    try:
        video_id = extract_video_code(youtube_video_url)
        
        if not video_id:
            return None, None

        # Retrieve the available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        transcript_text = ""
        transcript_language = target_language
        
        # Iterate over all available transcripts to find the most suitable one
        for transcript in transcript_list:
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

    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video. Please check if the video has captions or subtitles enabled.")
        return None, None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None

# Generate summary based on the prompt
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

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
                # Use a tailored prompt for English
                if target_language == 'en':
                    prompt = "Act as a YouTube video summarizer. Summarize the transcript of the video in 200 words: "
                else:
                    prompt = prompt_template.format(target_language)

                summary = generate_gemini_content(transcript_text, prompt)

                # Translate the summary only if the target language is not English
                if target_language != 'en':
                    translator = Translator()
                    summary = translator.translate(summary, dest=target_language).text

                st.markdown("## Detailed Notes:")
                st.write(f"**Language:** {target_language}")
                st.write(summary)

