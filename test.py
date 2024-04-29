from openai import OpenAI
from dotenv import load_dotenv
import os
from PIL import Image
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

# # Define the system message
# system_msg = 'You are a helpful assistant who understands data science.'

# # Define the user message
# user_msg = 'Create a small dataset about total sales over the last year. The format of the dataset should be a data frame with 12 rows and 2 columns. The columns should be called "month" and "total_sales_usd". The "month" column should contain the shortened forms of month names from "Jan" to "Dec". The "total_sales_usd" column should contain random numeric values taken from a normal distribution with mean 100000 and standard deviation 5000. Provide Python code to generate the dataset, then provide the output in the format of a markdown table.'

# # Create a dataset using GPT
# response = client.chat.completions.create(model="gpt-3.5-turbo",
#                                             messages=[{"role": "system", "content": system_msg},
#                                          {"role": "user", "content": user_msg}])

# print(response)

# response = client.images.generate(
#    model="dall-e-3",
#    prompt="A lush, vibrant forest filled with colorful flowers, sparkling streams, and magical creatures. The sun filters through the canopy of trees, creating a dreamlike atmosphere.",
#    size="1024x1024",
#    quality="standard",
#    n=1,
# )
# image_url = response.data[0].url
# print(image_url)

# text = "In a galaxy far, far away, there was a child who loved nothing more than to gaze at the stars and draw what they saw in their notebook."

# # Call OpenAI's text-to-speech API
# response = client.audio.speech.create(
#    model="tts-1",
#    voice="alloy",
#    input=text
# )

# response.stream_to_file("test.mp3")


# Define target dimensions
target_width = 1920
target_height = 1080


def make_video(image_files, audio_files, save_path):
   clips = []
   # Iterate through the image and audio files and create pairs of clips
   for image_path, audio_path in zip(image_files, audio_files):
      audio_clip = AudioFileClip(audio_path)
      # Load image clip
      image_clip = ImageClip(image_path).set_duration(audio_clip.duration)

      clips.append(image_clip.set_audio(audio_clip))

   # Concatenate the final clips
   final_video = concatenate_videoclips(clips)

   # Export the final video
   final_video.write_videofile(save_path, codec='libx264', fps=24)

image_paths = [
   "image0.png",
   "image1.png",
   "image2.png",
   "image3.png",
   "image4.png",
   "image5.png",
]
audio_paths = [
   "audio0.mp3",
   "audio1.mp3",
   "audio2.mp3",
   "audio3.mp3",
   "audio4.mp3",
   "audio5.mp3",
]
make_video(image_paths, audio_paths, "temp.mp4")