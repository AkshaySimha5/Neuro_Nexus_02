from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
from merge import parse, summarize_article  # Import summarize_article

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

@app.route('/fetch_article', methods=['GET'])
def fetch_article():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400
    
    try:
        # Extract title and content using parse()
        title, content = parse(url=url)

        if not content:
            return jsonify({'error': 'Failed to extract content from the article'}), 500

        # Summarize the content
        summary = summarize_article(content)
        print(summary)
        # Return the title and summary as a JSON response
        return jsonify({'title': title, 'summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
