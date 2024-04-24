from flask import Flask, render_template, request, jsonify
import requests
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_KEY')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def handle_data():
    data = request.json
    print("Received data:", data)  # Debugging: Print received data

    # Replace 'your_openai_api_key_here' with your actual OpenAI API key
    api_key = 
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    # Constructing the prompt from received data
    prompt_text = construct_prompt(data)

    system_msg = 'You are an assistant that writes childrens story books'

    # Create a dataset using GPT
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=[{"role": "system", "content": system_msg},
                                            {"role": "user", "content": prompt_text}])
    # response = requests.post(
    #     'https://api.openai.com/v1/engines/text-davinci-003/completions',
    #     headers=headers,
    #     json={
    #         'model': 'gpt-3.5-turbo-0125',  # You can use "gpt-3.5-turbo" or other appropriate model
    #         'prompt': prompt_text,
    #         'max_tokens': 150
    #     }
    # )

    # Check if the API call was successful
    if response.status_code == 200:
        output = response.json()['choices'][0]['text'].strip()
        print(output)
        return jsonify({'status': 'success', 'message': 'Data processed', 'result': output})
    else:
        print("Something went wrong")
        return jsonify({'status': 'error', 'message': 'Failed to process data with AI'})

def construct_prompt(data):
    # Construct a coherent prompt based on the collected data
    # This is a simple example; you should tailor this function to fit your specific needs
    prompt = f"Create a short childrens story based on the following settings:\nGenre: {data.get('genreQuestion')}\nSetting: {data.get('settingQuestion')}\nCharacter: {data.get('mainCharacterQuestion')}\nConflict: {data.get('mainConflictQuestion')}\nTone: {data.get('storyToneQuestion')}\nEnding: {data.get('storyEndingQuestion')}\n"
    return prompt

if __name__ == '__main__':
    app.run(debug=True)
