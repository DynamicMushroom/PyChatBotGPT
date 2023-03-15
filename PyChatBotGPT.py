import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up the OpenAI model
model_engine = "davinci-codex"  # choose the model engine you want to use
model_prompt = "You are ChatGPT, a large language model trained by OpenAI. Help answer questions and engage in conversation."  # prompt to start the conversation
chat_history = []  # keep track of the conversation history
max_history_tokens = 1500  # maximum number of tokens to keep in the chat history

def generate_response(prompt, model_engine, chat_history):
    # Check if the prompt is empty or contains only whitespace
    if not prompt.strip():
        return ""

    # Prepare conversation history for the API
    conversation = "".join([f"{entry}\n" for entry in chat_history])

    # Generate a response using OpenAI's API
    response = openai.Completion.create(
        engine=model_engine,
        prompt=f"{model_prompt}\n{conversation}User: {prompt}\nAssistant:",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n"]
    )

    # Decode the response and remove the newline characters
    text = response.choices[0].text
    text = text.strip()

    # Add the response to the chat history
    chat_history.append(f"Assistant: {text}")

    return text

# Start the conversation
print(model_prompt)
while True:
    # Get user input
    user_input = input("> ")

    # Add user input to the chat history
    chat_history.append(f"User: {user_input}")

    # Truncate the chat history if necessary
    if len("".join(chat_history)) > max_history_tokens:
        chat_history.pop(0)

    # Generate a response
    response = generate_response(user_input, model_engine, chat_history)

    # Print the response
    print(response)
