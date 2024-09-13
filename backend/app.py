from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
from article_extractor import parse  # Import the parse function from article_extractor

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

@app.route('/fetch_article', methods=['GET'])
def fetch_article():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400
    try:
        title, content = parse(url=url)
        return jsonify({'title': title, 'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
