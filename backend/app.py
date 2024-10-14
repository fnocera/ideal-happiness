# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from test_factory import TestFactory

app = Flask(__name__)
CORS(app)

# Initialize TestFactory instance
test_factory = TestFactory()

@app.route('/intents', methods=['GET'])
def list_intents():
    return jsonify({'intents': test_factory.intents})

@app.route('/generate_for_intent', methods=['POST'])
def generate_for_intent():
    data = request.get_json()
    intent = data.get('intent')
    function_calls, spec_portions = test_factory.generate_for_intent(intent)
    return jsonify({
        'function_calls': function_calls,
        'spec_portions': spec_portions
    })

@app.route('/persist_output', methods=['POST'])
def persist_output():
    data = request.get_json()
    intent = data.get('intent')
    corrected_function_calls = data.get('corrected_function_calls')
    test_factory.persist_output(intent, corrected_function_calls)
    return jsonify({'status': 'success'})

@app.route('/upload_intents', methods=['POST'])
def upload_intents():
    file = request.files['file']
    file.save(test_factory.intents_file_path)
    test_factory.intents = test_factory.load_intents()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
