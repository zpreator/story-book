from flask import Flask, render_template, request, url_for, jsonify, session
import os
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()

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

    # Create a dataset using GPT
    response = client.chat.completions.create(model="gpt-3.5-turbo",
                                            messages=[{"role": "system", "content": system_msg},
                                            {"role": "user", "content": prompt_text}])

    # Check if the API call was successful
    if response.choices[0].finish_reason == "stop":
        output = response.choices[0].message.content
        # print(output)
        session['story'] = output
        return jsonify({'status': 'success', 'redirect_url': url_for('display_story')})
    else:
        print("Something went wrong")
        return jsonify({'status': 'error', 'message': 'Failed to process data with AI'})

@app.route('/story')
def display_story():
    story = session.get('story', 'No story found')

    # Parse the story and ask dalle for images
    results = extract_text_with_brackets(story)
    pages = []
    for description, text in results:
        response = client.images.generate(
            model="dall-e-3",
            prompt=description,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        pages.append({"image": image_url, "text": text})
    return render_template('story.html', pages=pages)

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
    \nPlease divide the story into hypothetical pages, where each page
    \nis only one to two sentences. For each page, also include a section
    \npreceding it describing the hypothetical image on that page and wrap that
    \ntext in square brackets. Make sure each page has a visual description, and text.
    \n
    \nKeep the language easy to read for kids of ages 10 and up, but keep the content
    \nentertaining for both the kids and adults.
    \n
    \nOnly generate a maximum of 6 pages for the short story."""
    return prompt

if __name__ == '__main__':
    app.run(debug=True)
