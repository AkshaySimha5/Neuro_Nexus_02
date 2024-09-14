from flask import Flask, jsonify, request
from flask_cors import CORS
from final_merge import parse, summarize_article, classify_text, classify_sentiment  # Import functions

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

        # Classify the content for category and sentiment
        category = classify_text(content)
        sentiment = classify_sentiment(summary)

        # Return the title, summary, category, and sentiment as a JSON response
        return jsonify({'title': title, 'summary': summary, 'category': category, 'sentiment': sentiment})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
