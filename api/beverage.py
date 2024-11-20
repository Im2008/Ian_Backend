from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../../instance/voting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define models
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beverage = db.Column(db.String(50), nullable=False)
    reasoning = db.Column(db.String(200), nullable=True)

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suggestion = db.Column(db.String(100), nullable=False)

# Create the database
with app.app_context():
    db.create_all()

# Add CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Endpoint to submit a vote
@app.route('/api/vote', methods=['POST'])
def submit_vote():
    data = request.json
    beverage = data.get('beverage')
    reasoning = data.get('reasoning', '')
    if beverage:
        new_vote = Vote(beverage=beverage, reasoning=reasoning)
        db.session.add(new_vote)
        db.session.commit()
        return jsonify({'message': 'Vote submitted successfully'}), 200
    return jsonify({'error': 'Beverage not specified'}), 400

# Endpoint to submit a suggestion
@app.route('/api/suggest', methods=['POST'])
def submit_suggestion():
    data = request.json
    suggestion = data.get('suggestion')
    if suggestion:
        new_suggestion = Suggestion(suggestion=suggestion)
        db.session.add(new_suggestion)
        db.session.commit()
        return jsonify({'message': 'Suggestion submitted successfully'}), 200
    return jsonify({'error': 'Suggestion not specified'}), 400

# Endpoint to get voting results
@app.route('/api/results', methods=['GET'])
def get_results():
    votes = Vote.query.all()
    results = {}
    for vote in votes:
        if vote.beverage in results:
            results[vote.beverage] += 1
        else:
            results[vote.beverage] = 1
    return jsonify(results)

# Endpoint to get suggestions
@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    suggestions = Suggestion.query.all()
    return jsonify([s.suggestion for s in suggestions])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8887, debug=True)
