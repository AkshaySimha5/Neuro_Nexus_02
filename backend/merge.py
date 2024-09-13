import requests
import textwrap
from extractor import *
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import json

def parse(url='', html='', threshold=0.9, output='html', **kwargs):
    """
    Extract article by URL or HTML.

    :param url: URL for the article.
    :param html: HTML for the article.
    :param threshold: The ratio of text to the entire document, default 0.9.
    :param output: Result output format, supports `markdown` and `html, default ``html``
    :param **kwargs: Optional arguments that `requests.get` takes.
    :return: :class:`tuple` object containing (title, article_content)
    """

    # Handle missing URL or HTML case
    if not url and not html:
        raise ValueError("Either 'url' or 'html' must be provided.")

    try:
        # Create an Extractor instance, either using the URL or provided HTML
        ext = Extractor(url=url, html=html, threshold=threshold, output=output, **kwargs)

        # Parse the content and return the title and article content
        return ext.parse()

    except requests.RequestException as e:
        print(f"Error occurred while making the request: {e}")
        return '', ''
    except Exception as e:
        print(f"An error occurred: {e}")
        return '', ''

def summarize_article(article):
    """
    Summarize the given article content.

    :param article: The article content as a string.
    :return: The summarized content.
    """
    
    # Initialize the pipeline and model
    pipe = pipeline("text2text-generation", model="Yooniii/Article_summarizer")
    tokenizer = AutoTokenizer.from_pretrained("Yooniii/Article_summarizer")
    model = AutoModelForSeq2SeqLM.from_pretrained("Yooniii/Article_summarizer")

    # Check if a GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # Move the model to the GPU
    model = model.to(device)

    # Tokenize the input text and move the inputs to the GPU
    inputs = tokenizer.encode(article, return_tensors="pt", max_length=1024, truncation=True).to(device)

    # Generate the summary
    summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4)

    # Decode the summary (no need to move summary_ids back to the CPU, as decoding works on GPU tensors)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary

def send_http_payload(url, title, summary):
    """
    Sends the title and summary as an HTTP payload (JSON) to a specified URL.

    :param url: The URL of the API endpoint to send the payload.
    :param title: The title of the article.
    :param summary: The summarized content.
    :return: The response from the server.
    """
    payload = {
        "title": title,
        "summary": summary
    }

    headers = {
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response
    except requests.RequestException as e:
        print(f"Error occurred while sending the payload: {e}")
        return None

def save_to_file(filename, title, original_content, summary):
    """
    Save the original and summarized content into a text file with proper line breaks.

    :param filename: Name of the file to save the content.
    :param title: Title of the article.
    :param original_content: The full article content.
    :param summary: The summarized article content.
    """
    # Use textwrap to wrap long lines for better readability
    wrapper = textwrap.TextWrapper(width=80)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n\n")
        f.write("Original Content:\n")
        # Add line breaks in the original content for readability
        original_wrapped = wrapper.fill(original_content)
        f.write(original_wrapped + "\n\n")

        f.write("Summary:\n")
        # Add line breaks in the summary for readability
        summary_wrapped = wrapper.fill(summary)
        f.write(summary_wrapped + "\n")
# Example usage:
if __name__ == "__main__":
    article_url = 'https://www.bbc.com/news/articles/clywepq2eq2o'

    # Optional headers to mimic a browser request (some websites may require this)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Call the parse function with the URL and headers
    title, content = parse(url=article_url, headers=headers)

    if content:
        # Print the extracted title and content
        print("Title:", title)
        
        # Summarize the content
        summary = summarize_article(content)
        print("Summary:", summary)
        
        # Send the title and summary as an HTTP payload
        api_endpoint = 'http://127.0.0.1:5000/fetch_article'  # Flask API URL
  # Replace with your API endpoint
        response = send_http_payload(api_endpoint, title, summary)

        if response:
            print("Payload sent successfully. Response:", response.status_code, response.text)
        else:
            print("Failed to send the payload.")
    else:
        print("Failed to extract content.")
