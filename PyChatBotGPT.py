from flask import Flask, request, jsonify
import os
import openai
import json
import logging
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

#Enter your dotenv file name with your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setup logging
logging.basicConfig(filename='chat.log', level=logging.INFO)

# Flask and CORS app setup
app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": "*"}})


model_engine = "gpt-4"
model_prompt = "You are GPT-4, a large language model trained by OpenAI. Help answer questions and engage in conversation."
chat_history = []
max_history_tokens = 2000

#save history function
def save_history(chat_history, filename='history.json'):
    with open(filename, 'w') as f:
        json.dump(chat_history, f)
        
 #Load history function
def load_history(filename='history.json'):
    with open(filename, 'r') as f:
        return json.load(f)
    
#Response
def generate_response(prompt, model_engine, chat_history):
    if not prompt.strip():
        return ""

    conversation = "".join([f"{entry}\n" for entry in chat_history])

    try:
        response = openai.ChatCompletion.create(
            model=model_engine,
            messages=[
                {"role": "system", "content": model_prompt},
                {"role": "user", "content": f"{conversation}User: {prompt}"}
            ],
            max_tokens=2000,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n"]
        )
        text = response['choices'][0]['message']['content']
        text = text.strip()
        chat_history.append(f"Assistant: {text}")
    except openai.error.OpenAIError as e:
        text = f"Error: {e}"
        logging.error(text)
    
    return text

# Flask route to handle POST requests
@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['user_input']
    response = generate_response(user_input, model_engine, chat_history)
    return jsonify({'response': response})

# Main block to run the Flask app
if __name__ == "__main__":
    try:
        chat_history = load_history()
    except FileNotFoundError:
        pass
    
    app.run(port=3000)
