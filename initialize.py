from flask import Flask
from flask_cors import CORS

def create_app():
  app = Flask(__name__)
  # CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://palmerigarrett.github.io"]}}) # use with auth
  # CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://palmerigarrett.github.io", "https://palmerigarrett.github.io/merkle/"]}})
  # app.config['CORS_ALLOW_HEADERS'] = 'Content-Type' #replaces app.config['CORS_HEADERS']
  CORS(app, resources=r"/api/*")
  # app.config['CORS_HEADERS'] = 'Content-Type' # This is wrong
  return app