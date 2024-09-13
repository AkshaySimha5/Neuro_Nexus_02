from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline, AutoModelForSeq2SeqLM
import torch
import requests
import textwrap
from extractor import Extractor

# Function for text classification using a pre-trained model
def classify_text(text):
    """
    Classify the given text using a pre-trained model.

    :param text: The input text to classify.
    :return: Predicted class label.
    """
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("Yueh-Huan/news-category-classification-distilbert")
    model = AutoModelForSequenceClassification.from_pretrained("Yueh-Huan/news-category-classification-distilbert", from_tf=True)

    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    # Get model predictions (logits)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # Convert logits to predicted class
    predicted_class = torch.argmax(logits, dim=1).item()

    # Check if id2label mapping is available and return the predicted label
    if hasattr(model.config, 'id2label'):
        id2label = model.config.id2label
        return id2label[predicted_class]
    else:
        return predicted_class

# Function to parse article content by URL or HTML
def parse(url='', html='', threshold=0.9, output='html', **kwargs):
    """
    Extract article by URL or HTML.

    :param url: URL for the article.
    :param html: HTML for the article.
    :param threshold: The ratio of text to the entire document, default 0.9.
    :param output: Result output format, supports `markdown` and `html, default ``html`.
    :param **kwargs: Optional arguments that `requests.get` takes.
    :return: :class:tuple object containing (title, article_content)
    """
    if not url and not html:
        raise ValueError("Either 'url' or 'html' must be provided.")

    try:
        # Create an Extractor instance, either using the URL or provided HTML
        ext = Extractor(url=url, html=html, threshold=threshold, output=output, **kwargs)
        return ext.parse()
    except requests.RequestException as e:
        print(f"Error occurred while making the request: {e}")
        return '', ''
    except Exception as e:
        print(f"An error occurred: {e}")
        return '', ''

# Function to summarize an article
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

    # Decode the summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary

# Function to save content to a text file
def save_to_file(filename, title, original_content, summary):
    """
    Save the original and summarized content into a text file with proper line breaks.

    :param filename: Name of the file to save the content.
    :param title: Title of the article.
    :param original_content: The full article content.
    :param summary: The summarized article content.
    """
    wrapper = textwrap.TextWrapper(width=80)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n\n")
        f.write("Original Content:\n")
        original_wrapped = wrapper.fill(original_content)
        f.write(original_wrapped + "\n\n")
        f.write("Summary:\n")
        summary_wrapped = wrapper.fill(summary)
        f.write(summary_wrapped + "\n")

# Main function to classify an article's content and summarize it
if __name__ == "__main__":
    url = 'https://www.bbc.com/news/articles/clywepq2eq2o'

    # Optional headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Parse the article
    title, content = parse(url=url, headers=headers)

    if content:
        print("Title:", title)

        # Summarize the content
        summary = summarize_article(content)
        print("Summary:", summary)

        # Classify the content
        classification = classify_text(content)
        print(f"Classified as: {classification}")

        # Save the title, original content, summary, and classification to a text file
        filename = "article_summary.txt"
        save_to_file(filename, title, content, summary)
        print(f"Original and summarized content saved to {filename}")
    else:
        print("Failed to extract content.")
