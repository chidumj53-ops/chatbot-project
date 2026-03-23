import json
import random
import torch
import nltk
import os
from dotenv import load_dotenv
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

# ---------------- NLTK setup ----------------
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# ---------------- Load Gemini API ----------------
from google.genai import Client

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

gemini_client = Client(api_key=GEMINI_API_KEY)

# ---------------- Device ----------------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ---------------- Load intents ----------------
with open('intents.json', 'r') as f:
    intents = json.load(f)

# ---------------- Load trained model ----------------
FILE = "data.pth"
data = torch.load(FILE, map_location=device)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# ---------------- Chatbot info ----------------
bot_name = "Sam"
conversation_history = []


# ---------------- Gemini API call (concise) ----------------
def ask_gemini(history):
    messages = []
    for h in history[-10:]:
        messages.append(f"{h['role']}: {h['content']}")

    # Add instruction for concise response
    prompt = "Answer concisely in 1-2 sentences, without extra details.\n\n" + "\n".join(messages)

    try:
        models_list = gemini_client.models.list()
        gemini_models = [m.name for m in models_list if "gemini" in m.name.lower()]
        if not gemini_models:
            return "⚠️ No Gemini model available."
        model_name = gemini_models[0]

        response = gemini_client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print("Gemini Error:", e)
        return "⚠️ AI service unavailable."


# ---------------- Main chatbot response ----------------
def get_response(msg):
    # Save user message
    conversation_history.append({"role": "user", "content": msg})
    conversation_history[:] = conversation_history[-20:]  # keep last 20 messages

    # 1️⃣ Intent detection (high-confidence suggestions)
    intent_response = None
    try:
        sentence = tokenize(msg)
        X = bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)
        _, predicted = torch.max(output, dim=1)
        tag = tags[predicted.item()]
        prob = torch.softmax(output, dim=1)[0][predicted.item()]

        if prob.item() > 0.90:
            for intent in intents["intents"]:
                if tag == intent["tag"]:
                    intent_response = random.choice(intent["responses"])
                    break
    except Exception as e:
        print("Intent error:", e)

    # 2️⃣ Gemini AI response (if intent doesn't match)
    gpt_response = ask_gemini(conversation_history) if not intent_response else None

    # 3️⃣ Final response prioritization: Intent > Gemini
    final_response = intent_response or gpt_response

    # Save AI response in history
    conversation_history.append({"role": "assistant", "content": final_response})

    return final_response