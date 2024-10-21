from flask import Flask, request, jsonify, send_from_directory, render_template
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # Enable CORS to allow frontend-backend communication

# MongoDB Setup
client = MongoClient("mongodb+srv://singareddyprasadreddy6:tEfzVegOCmGxheE4@cluster0.0jd0e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['rule_engine']
rules_collection = db['rules']

# AST Node class
class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type
        self.left = left
        self.right = right
        self.value = value

    def to_dict(self):
        return {
            "type": self.type,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
            "value": self.value,
        }

# Route: Home (Serves the frontend)
@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

# Route: Create a new rule
@app.route('/create_rule', methods=['POST'])
def create_rule():
    data = request.json
    rule_string = data.get('rule')

    if not rule_string:
        return jsonify({"error": "Rule string is required"}), 400

    result = rules_collection.insert_one({"rule_string": rule_string})
    return jsonify({"message": "Rule created", "id": str(result.inserted_id)}), 201

# Route: Combine rules
@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    data = request.json
    rule_ids = data.get('rule_ids')

    if not rule_ids or not isinstance(rule_ids, list):
        return jsonify({"error": "A list of rule IDs is required"}), 400

    rules = rules_collection.find({"_id": {"$in": [ObjectId(rid) for rid in rule_ids]}})
    combined_rule_string = " OR ".join([rule['rule_string'] for rule in rules])

    result = rules_collection.insert_one({"rule_string": combined_rule_string})
    return jsonify({"message": "Rules combined", "id": str(result.inserted_id)}), 201

# Route: Evaluate a rule
@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    data = request.json
    rule_id = data.get('rule_id')
    attributes = data.get('attributes')

    if not rule_id or not attributes:
        return jsonify({"error": "Rule ID and attributes are required"}), 400

    rule = rules_collection.find_one({"_id": ObjectId(rule_id)})
    if not rule:
        return jsonify({"error": "Rule not found"}), 404

    try:
        result = eval(rule['rule_string'], {}, attributes)  # Use cautiously
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
