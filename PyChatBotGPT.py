from flask import Flask, request, jsonify
import os
import openai
import json
import logging
import boto3
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Enter your dotenv file name with your API key and AWS credentials
openai.api_key = os.getenv("OPENAI_API_KEY")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")
s3_key_name = os.getenv("S3_KEY_NAME")

# Setup logging
logging.basicConfig(filename='chat.log', level=logging.INFO)

# Flask and CORS app setup
app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": "*"}})

# AWS S3 Setup
s3 = boto3.client('s3',
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name=aws_region)

model_engine = "gpt-4"
model_prompt = "You are GPT-4, a large language model trained by OpenAI. Help answer questions and engage in conversation."
chat_history = []
max_history_tokens = 2000

# Save history function
def save_history(chat_history):
    s3.put_object(
        Body=json.dumps(chat_history),
        Bucket=s3_bucket_name,
        Key=s3_key_name
    )
        
# Load history function
def load_history():
    try:
        my_file = s3.get_object(
            Bucket=s3_bucket_name,
            Key=s3_key_name
        )
        return json.loads(my_file['Body'].read())
    except s3.exceptions.NoSuchKey:
        return []
    
# Response
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
    save_history(chat_history)  # Save the updated chat history to S3
    return jsonify({'response': response})

# Main block to run the Flask app
if __name__ == "__main__":
    chat_history = load_history()  # Load chat history from S3
    app.run(port=3000)
