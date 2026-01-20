import numpy as np
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import random
import string
import json

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class SimpleChatbot:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.words = []
        self.classes = []
        self.documents = []
        self.ignore_words = list(string.punctuation)
        self.model = {}
        
    def clean_text(self, text):
        """Clean and tokenize text"""
        tokens = word_tokenize(text.lower())
        tokens = [self.stemmer.stem(word) for word in tokens if word not in self.ignore_words]
        return tokens
    
    def bag_of_words(self, text, vocab):
        """Create bag of words array"""
        tokens = self.clean_text(text)
        bag = [1 if word in tokens else 0 for word in vocab]
        return np.array(bag)
    
    def train(self, training_data):
        """Train the chatbot with provided data"""
        print("Training chatbot...")
        
        # Process intents
        for intent in training_data['intents']:
            tag = intent['tag']
            if tag not in self.classes:
                self.classes.append(tag)
            
            for pattern in intent['patterns']:
                tokens = self.clean_text(pattern)
                self.words.extend(tokens)
                self.documents.append((tokens, tag))
        
        # Remove duplicates and sort
        self.words = sorted(set(self.words))
        self.classes = sorted(set(self.classes))
        
        # Create training data
        training = []
        output_empty = [0] * len(self.classes)
        
        for doc in self.documents:
            bag = []
            word_patterns = doc[0]
            
            for word in self.words:
                bag.append(1 if word in word_patterns else 0)
            
            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            
            training.append([bag, output_row])
        
        # Simple model storage
        self.model = {
            'words': self.words,
            'classes': self.classes,
            'intents': training_data['intents']
        }
        
        print(f"Training complete! Learned {len(self.words)} words and {len(self.classes)} intents.")
    
    def get_response(self, user_input):
        """Get response for user input"""
        if not self.model:
            return "I haven't been trained yet!"
        
        # Calculate similarity
        input_bag = self.bag_of_words(user_input, self.model['words'])
        
        # Find best matching intent
        best_match = None
        highest_similarity = 0
        
        for intent in self.model['intents']:
            for pattern in intent['patterns']:
                pattern_bag = self.bag_of_words(pattern, self.model['words'])
                similarity = np.dot(input_bag, pattern_bag) / (np.linalg.norm(input_bag) * np.linalg.norm(pattern_bag) + 1e-10)
                
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = intent
        
        # Return response if similarity is high enough
        if best_match and highest_similarity > 0.3:
            return random.choice(best_match['responses'])
        else:
            return "I'm not sure how to respond to that. Could you try rephrasing?"
    
    def debug_info(self):
        """Return debug information about the chatbot"""
        return {
            'vocabulary_size': len(self.words),
            'intents': self.classes,
            'documents_count': len(self.documents)
        }