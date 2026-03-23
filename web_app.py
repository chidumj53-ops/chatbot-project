from flask import Flask, render_template, request, session
from chat import get_response, conversation_history

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def chatbot_response():
    msg = request.args.get('msg')

    if "history" not in session:
        session["history"] = []

    conversation_history.clear()
    conversation_history.extend(session["history"])

    response = get_response(msg)

    session["history"] = conversation_history.copy()
    return response

if __name__ == "__main__":
    app.run(debug=True)