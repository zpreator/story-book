from flask import Flask, render_template, request, url_for, jsonify, session, send_file, Response
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import re
import time
from pathlib import Path
from tqdm import tqdm
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import requests
from PIL import Image
from io import BytesIO

load_dotenv()

DEBUG = os.getenv("DEBUG", True)
STATIC = os.path.join(os.path.split(__file__)[0], "static")

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def handle_data():
    data = request.json
    print("Received data:", data)  # Debugging: Print received data

    # Constructing the prompt from received data
    prompt_text = construct_prompt(data)

    system_msg = 'You are an assistant that writes childrens story books'

    if DEBUG:
        output = """
The Resourceful Inventor on the Mysterious Island

[A picture of a lush, green island with colorful flowers and a hidden cave entrance]

In a faraway, mysterious island, there lived a clever inventor who loved creating new gadgets. One day, he stumbled upon a hidden cave, sparking his curiosity.

[A picture of the inventor exploring the dark cave with a flashlight]

As the inventor ventured into the dark cave with his trusty flashlight, he discovered peculiar markings on the walls. It was a mystery waiting to be solved!

[A picture of the inventor examining ancient artifacts found in the cave]

Among the ancient artifacts inside the cave, the inventor found a map leading to a hidden treasure. Excited and determined, he knew he had to embark on an adventure.

[A picture of the inventor navigating through a dense jungle with his makeshift compass]

Equipped with his inventive compass made from sticks and leaves, the resourceful inventor bravely journeyed through the dense jungle, following the map's clues.

[A picture of the inventor uncovering a hidden treasure chest filled with glowing gems]

After many challenges and obstacles, the inventor finally reached the treasure chest hidden deep within the heart of the island. Inside, he found shimmering gems and a note that read, "The greatest treasure is not gold, but the journey itself."

[A picture of the inventor sailing back home on a boat, with a smile on his face]

With a heart full of joy and wisdom gained from his adventure, the inventor sailed back home, knowing that true treasures are found in the experiences we live and the lessons we learn.
"""
        session['story'] = output
        return jsonify({'status': 'success'})
    else:
        # Create a dataset using GPT
        response = client.chat.completions.create(model="gpt-3.5-turbo",
                                                messages=[{"role": "system", "content": system_msg},
                                                {"role": "user", "content": prompt_text}])

        # Check if the API call was successful
        if response.choices[0].finish_reason == "stop":
            output = response.choices[0].message.content
            
            session['story'] = output
            return jsonify({'status': 'success'})
        else:
            print("Something went wrong")
            return jsonify({'status': 'error', 'message': 'Failed to process data with AI'})

@app.route('/story', methods=['POST'])
def display_story():
    story = session.get('story', 'No story found')

    print(story)

    # Parse the story and ask dalle for images
    results = extract_text_with_brackets(story)
    pages = []
    count = 0
    image_paths = []
    audio_paths = []
    for description, text in tqdm(results):
        if DEBUG:
            pages.append({"image": url_for('static', filename=f"test/image{count}.png"), "text": text, "description": description})
        else:
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=description,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
                pages.append({"image": image_url, "text": text, "description": description})
            except openai.RateLimitError:
                time.sleep(60)
                response = client.images.generate(
                    model="dall-e-2",
                    prompt=description,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
                pages.append({"image": image_url, "text": text, "description": description})
        count += 1
            # image_path = f"image{count}.png"
            # audio_path = f"audio{count}.mp3"
            # save_text_to_speech(text, audio_path)
            # response = requests.get(image_url)
            # image = Image.open(BytesIO(response.content))
            # image.save(image_path)
            
            # image_paths.append(image_path)
            # audio_paths.append(audio_path)

    # make_video(image_paths, audio_paths, "temp.mp4")
    session["pages"] = pages
    return jsonify({'status': 'success', 'pages': pages})

@app.route('/tts', methods=['POST'])
def text_to_speech():
    # Get text from POST request
    text = request.form['text']
    
    # Specify the path for the speech file
    save_file = "speech.mp3"

    if not DEBUG:
        save_text_to_speech(text, save_file)
    
    # Return the speech file
    return send_file(str(save_file), as_attachment=True)

@app.route("/export")
def export():
    pages = session.get('pages')
    if pages:
        image_paths = []
        audio_paths = []
        for i, page in enumerate(pages):
            image_path = f"image{i}.png"
            audio_path = f"audio{i}.mp3"
            save_text_to_speech(page["text"], audio_path)
            if "http" in page["image"]:
                response = requests.get(page["image"])
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(os.path.join(STATIC, "test", page["image"].split("/")[-1]))
            image.save(image_path)
            
            image_paths.append(image_path)
            audio_paths.append(audio_path)
        make_video(image_paths, audio_paths, "video.mp4")
        return send_file("video.mp4", as_attachment=True)
    return '', 204

@app.route("/support")
def support():
    return render_template('support.html')

def save_text_to_speech(text, save_path):
    # Call OpenAI's text-to-speech API
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    
    # Stream the response to a file
    response.stream_to_file(str(save_path))

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

def extract_text_with_brackets(text):
    # Use a regular expression to find all bracketed sections and the following paragraphs
    pattern = r'\[(.*?)\]\n*\n*(.*?)\n*(?=\n\[|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Create a list of tuples where each tuple contains the bracketed text and the following paragraph or None
    extracted = []
    for match in matches:
        section, following_paragraph = match
        if not following_paragraph.strip():  # Check if the following paragraph is empty or only contains whitespace
            following_paragraph = None
        extracted.append((section, following_paragraph))
    
    return extracted

def construct_prompt(data):
    # Construct a coherent prompt based on the collected data
    # This is a simple example; you should tailor this function to fit your specific needs
    prompt = f"""Create a short childrens story based on the following settings:
    \nGenre: {data.get('genreQuestion')}
    \nSetting: {data.get('settingQuestion')}
    \nCharacter: {data.get('mainCharacterQuestion')}
    \nConflict: {data.get('mainConflictQuestion')}
    \nTone: {data.get('storyToneQuestion')}
    \nEnding: {data.get('storyEndingQuestion')}
    \n
    \nPlease divide the story into pages, where each page contains a description of the
    \nimage for that page of the story book, as well as the text for the story. The description 
    \nof the image should be in square brackets and should only talk about the scene. Leave the regular
    \nstory component as text. For the text on each page, keep it to only 1 - 2 sentences.
    \nThere is no need to specify page numbers, and make sure each page has part of the story, and a
    \ndescription of the image.
    \n
    \nIn your description of the image, don't use the names of the characters, instead describe
    \nthem with great detail everytime. Make sure the details stay the same in different sections.
    \n
    \nKeep the language easy to read for kids of ages 10 and up, but keep the content
    \nentertaining for both the kids and adults.
    \n
    \nWrite a title first, then only generate a maximum of 6 pages for the short story. Make sure each page
    \nhas an associated visual description in square brackets and text from the story.
    \n
    \nHere is a short example of 2 pages:
    \n
    \nThe Observing Turtle
    \n
    \n[A picture of an observatory overlooking a city with the stars showing, a turtle is seen looking through a telescope]
    \n
    \nOnce upon a time, in an observatory, there lived a turtle that liked looking at the stars. He always
    \nspent his time with his favorite telescope.
    \n
    \n[A picture of a shooting star over a turtle with a telescope]
    \n
    \nOne day, the turtle observed a shooting star. He decided to make a wish.
    """
    return prompt

if __name__ == '__main__':
    # Use the PORT environment variable provided by Heroku
    port = int(os.environ.get('PORT', 5001))

    app.run(debug=True, port=port, host='0.0.0.0')
