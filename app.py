from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Database configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "voting.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beverage = db.Column(db.String(50), nullable=False)
    reasoning = db.Column(db.String(200), nullable=True)

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suggestion = db.Column(db.String(100), nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

# Routes
@app.route('/api/vote', methods=['POST'])
def submit_vote():
    data = request.get_json()
    beverage = data.get('beverage')
    reasoning = data.get('reasoning', '')

    if not beverage:
        return jsonify({'error': 'Beverage not specified'}), 400

    new_vote = Vote(beverage=beverage, reasoning=reasoning)
    db.session.add(new_vote)
    db.session.commit()

    return jsonify({'message': 'Vote submitted successfully'}), 200

@app.route('/api/suggest', methods=['POST'])
def submit_suggestion():
    data = request.get_json()
    suggestion = data.get('suggestion')

    if not suggestion:
        return jsonify({'error': 'Suggestion not specified'}), 400

    new_suggestion = Suggestion(suggestion=suggestion)
    db.session.add(new_suggestion)
    db.session.commit()

    return jsonify({'message': 'Suggestion submitted successfully'}), 200

@app.route('/api/results', methods=['GET'])
def get_results():
    votes = Vote.query.all()
    results = {}

    for vote in votes:
        if vote.beverage in results:
            results[vote.beverage] += 1
        else:
            results[vote.beverage] = 1

    return jsonify(results), 200

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    suggestions = Suggestion.query.all()
    suggestion_list = [s.suggestion for s in suggestions]
    return jsonify(suggestion_list), 200

# Main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8887, debug=True)
