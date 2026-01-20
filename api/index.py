"""
Super Simple Chatbot for Vercel - No NLTK, Pure Python
"""
import json
import random
import re
from http.server import BaseHTTPRequestHandler
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Simple Chatbot Class
class SimpleChatbot:
    def __init__(self):
        self.intents = self.load_intents()
        
    def load_intents(self):
        """Load chatbot intents"""
        return {
            "greeting": {
                "patterns": ["hello", "hi", "hey", "good morning", "good afternoon"],
                "responses": ["Hello! How can I help you?", "Hi there! What can I do for you?", "Hey! How are you doing?"]
            },
            "goodbye": {
                "patterns": ["bye", "goodbye", "see you", "take care"],
                "responses": ["Goodbye! Have a great day!", "See you later!", "Take care!"]
            },
            "thanks": {
                "patterns": ["thank you", "thanks", "thank you so much"],
                "responses": ["You're welcome!", "My pleasure!", "Happy to help!"]
            },
            "name": {
                "patterns": ["what is your name", "who are you", "what should I call you"],
                "responses": ["I'm ChatBot!", "You can call me ChatBot!", "I'm your friendly chatbot!"]
            },
            "help": {
                "patterns": ["help", "what can you do", "how can you help"],
                "responses": ["I can chat with you and answer simple questions!", "I'm here to help you learn about chatbots!"]
            },
            "courses": {
                "patterns": ["what courses", "what can I learn", "subjects", "curriculum"],
                "responses": ["We offer: Python, Flask, NLP basics, and chatbot development!", "You can learn web development, machine learning, and NLP!"]
            },
            "nlp": {
                "patterns": ["what is nlp", "explain natural language processing"],
                "responses": ["NLP is Natural Language Processing - it helps computers understand human language!", "NLP stands for Natural Language Processing, a field of AI!"]
            },
            "creator": {
                "patterns": ["who created you", "who made you", "who built you"],
                "responses": ["I was created by students learning Flask deployment!", "I'm a student project for learning Vercel deployment!"]
            },
            "vercel": {
                "patterns": ["what is vercel", "tell me about vercel", "vercel deployment"],
                "responses": ["Vercel is a cloud platform for static sites and serverless functions!", "I'm deployed on Vercel - it's great for hosting web applications!"]
            }
        }
    
    def simple_tokenize(self, text):
        """Simple text tokenization"""
        text = text.lower().strip()
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        # Split into words
        words = text.split()
        return words
    
    def get_similarity(self, words1, words2):
        """Calculate word overlap similarity"""
        if not words1 or not words2:
            return 0
        
        set1 = set(words1)
        set2 = set(words2)
        
        common = len(set1.intersection(set2))
        total = len(set1.union(set2))
        
        return common / total if total > 0 else 0
    
    def get_response(self, user_message):
        """Get response for user message"""
        user_words = self.simple_tokenize(user_message)
        
        best_match = None
        best_score = 0
        
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data["patterns"]:
                pattern_words = self.simple_tokenize(pattern)
                score = self.get_similarity(user_words, pattern_words)
                
                if score > best_score:
                    best_score = score
                    best_match = intent_name
        
        # Return response if good match found
        if best_match and best_score > 0.3:
            return random.choice(self.intents[best_match]["responses"])
        else:
            fallbacks = [
                "I'm not sure I understand. Can you rephrase?",
                "That's interesting! Tell me more.",
                "I'm still learning. Could you ask differently?",
                "Could you explain that in another way?"
            ]
            return random.choice(fallbacks)

# Initialize chatbot globally
chatbot = SimpleChatbot()

# Vercel Serverless Function Handler
class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/':
            self.serve_home()
        elif self.path == '/health':
            self.serve_health()
        elif self.path == '/api/info':
            self.serve_api_info()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path == '/api/chat':
            self.handle_chat()
        elif self.path == '/api/train':
            self.handle_train()
        else:
            self.send_error(404, "Not Found")
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def serve_home(self):
        try:
            # Read HTML file
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Error loading page: {str(e)}")
    
    def serve_health(self):
        response = {
            "status": "healthy",
            "service": "Chatbot API",
            "version": "1.0.0",
            "intents": len(chatbot.intents)
        }
        self.send_json_response(200, response)
    
    def serve_api_info(self):
        response = {
            "name": "Vercel Chatbot",
            "description": "Simple chatbot deployed on Vercel",
            "endpoints": {
                "GET /": "Home page",
                "POST /api/chat": "Chat with bot",
                "POST /api/train": "Retrain bot",
                "GET /health": "Health check",
                "GET /api/info": "API information"
            }
        }
        self.send_json_response(200, response)
    
    def handle_chat(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_message = data.get('message', '').strip()
            
            if not user_message:
                response = {
                    "response": "Please enter a message!",
                    "status": "error"
                }
            else:
                bot_response = chatbot.get_response(user_message)
                response = {
                    "response": bot_response,
                    "status": "success",
                    "user_message": user_message
                }
            
            self.send_json_response(200, response)
            
        except json.JSONDecodeError:
            self.send_json_response(400, {"error": "Invalid JSON"})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
    
    def handle_train(self):
        try:
            # Reload intents (in real app, you might load from file)
            chatbot.intents = chatbot.load_intents()
            
            response = {
                "status": "success",
                "message": "Chatbot trained successfully!",
                "intents_count": len(chatbot.intents)
            }
            
            self.send_json_response(200, response)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
    
    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        error_response = {
            "error": message,
            "status_code": code
        }
        self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    # Override log_message to prevent logging to stderr
    def log_message(self, format, *args):
        pass

# Vercel expects this specific signature
def handler(request, response):
    # This is the function Vercel will call
    import io
    
    # Create a mock HTTP request handler
    class VercelRequestHandler:
        def __init__(self, request, response):
            self.request = request
            self.response = response
            self.headers = {}
            
        def handle(self):
            # Create a BaseHTTPRequestHandler instance
            h = Handler(
                io.BytesIO(),
                (self.request['headers'].get('host', ''), 80),
                self
            )
            
            # Set up the handler
            h.requestline = f"{self.request['method']} {self.request['path']} HTTP/1.1"
            h.command = self.request['method']
            h.path = self.request['path']
            h.headers = self.request['headers']
            
            # Handle the request
            if h.command == 'GET':
                h.do_GET()
            elif h.command == 'POST':
                h.do_POST()
            elif h.command == 'OPTIONS':
                h.do_OPTIONS()
            else:
                h.send_error(405, "Method not allowed")
            
            return self.response
            
        def makefile(self, *args, **kwargs):
            return io.BytesIO()
    
    # Handle the request
    handler_instance = VercelRequestHandler(request, response)
    return handler_instance.handle()

# For local testing
if __name__ == "__main__":
    from http.server import HTTPServer
    port = 8080
    server = HTTPServer(('localhost', port), Handler)
    print(f"Server running on http://localhost:{port}")
    server.serve_forever()
