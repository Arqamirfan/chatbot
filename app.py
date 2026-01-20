from flask import Flask, render_template, request, jsonify
from nlp_utils import SimpleChatbot
import json
import os

app = Flask(__name__)
chatbot = SimpleChatbot()

# Load training data
def load_training_data():
    data_path = os.path.join(os.path.dirname(__file__), 'training_data.json')
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            return json.load(f)
    return {
        "intents": [
            {
                "tag": "greeting",
                "patterns": ["Hello", "Hi", "Hey", "Good morning", "Good afternoon"],
                "responses": ["Hello! How can I help you?", "Hi there! What can I do for you?", "Hey! How are you doing?"]
            },
            {
                "tag": "goodbye",
                "patterns": ["Bye", "Goodbye", "See you later", "Take care"],
                "responses": ["Goodbye! Have a great day!", "See you later!", "Take care!"]
            },
            {
                "tag": "thanks",
                "patterns": ["Thank you", "Thanks", "Thanks a lot", "I appreciate it"],
                "responses": ["You're welcome!", "My pleasure!", "Glad I could help!"]
            },
            {
                "tag": "name",
                "patterns": ["What is your name?", "Who are you?", "What should I call you?"],
                "responses": ["I'm your friendly chatbot!", "You can call me ChatBot!", "I'm a simple chatbot created to help students learn NLP!"]
            },
            {
                "tag": "help",
                "patterns": ["Help", "What can you do?", "How can you help me?", "What are your functions?"],
                "responses": ["I can help you learn about chatbots and NLP! Try asking me about my features or just chat with me!", "I'm a basic chatbot that demonstrates NLP concepts. Ask me questions or try different greetings!"]
            },
            {
                "tag": "courses",
                "patterns": ["What courses do you offer?", "What can I learn?", "Subjects", "Curriculum"],
                "responses": ["We offer courses in: 1. Python Programming 2. Web Development 3. Machine Learning 4. Natural Language Processing", "You can learn: Python, Flask, NLP basics, and chatbot development in this course!"]
            }
        ]
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        
        if not user_message:
            return jsonify({'response': 'Please type a message!'})
        
        # Get chatbot response
        response = chatbot.get_response(user_message)
        
        return jsonify({
            'response': response,
            'user_message': user_message
        })
    except Exception as e:
        return jsonify({'response': f'Sorry, I encountered an error: {str(e)}'})

@app.route('/train', methods=['POST'])
def train():
    try:
        data = load_training_data()
        chatbot.train(data)
        return jsonify({'status': 'success', 'message': 'Chatbot trained successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Load and train chatbot on startup
    training_data = load_training_data()
    chatbot.train(training_data)
    print("Chatbot trained and ready!")
    app.run(debug=True, port=5000)