from flask import Flask, render_template, request, jsonify, make_response
from main.json_parser import print_json, testParser
import json

# init flask app
app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def home():
    return "Hello, I am the metric connector. Try a POST to /api/v1/deploy"

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/api/v1/deploy/list', methods=['GET'])
def listDeployPoints():
    with open('./data/aggregation.json') as file:
        print("Printing aggregated json...")
        aggregated_json = json.load(file)
        print_json(aggregated_json)
        return jsonify(aggregated_json)

@app.route('/api/v1/deploy', methods=['POST'])
def deploy():
    if not request.json:
        print_json(request.json)
        print("ERROR: Hmm, Are you sure you passed a json ?")
        return "ERROR: Hmm, Are you sure you passed a json ?"
    else:
        testParser(request.json)
        return "Okay, cool!"

if __name__ == '__main__':
    app.run()