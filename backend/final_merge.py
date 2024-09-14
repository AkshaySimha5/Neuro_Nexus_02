from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline, AutoModelForSeq2SeqLM
import torch
import requests
import textwrap
from extractor import Extractor
import torch.nn.functional as F

# Function for text classification using a pre-trained model (category classification)
def classify_text(text):
    tokenizer = AutoTokenizer.from_pretrained("Yueh-Huan/news-category-classification-distilbert")
    model = AutoModelForSequenceClassification.from_pretrained("Yueh-Huan/news-category-classification-distilbert", from_tf=True)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()
    
    # Check if id2label mapping is available and return the predicted label
    if hasattr(model.config, 'id2label'):
        id2label = model.config.id2label
        return id2label[predicted_class]
    else:
        return predicted_class

# Function for sentiment classification using a pre-trained model
def classify_sentiment(text):
    tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
    model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    probabilities = F.softmax(logits, dim=-1)
    predicted_class = torch.argmax(probabilities, dim=-1) + 1
    sentiment_labels = ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"]
    return sentiment_labels[predicted_class.item() - 1]

# Function to parse article content by URL or HTML
def parse(url='', html='', threshold=0.9, output='html', **kwargs):
    if not url and not html:
        raise ValueError("Either 'url' or 'html' must be provided.")
    try:
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
    tokenizer = AutoTokenizer.from_pretrained("Yooniii/Article_summarizer")
    model = AutoModelForSeq2SeqLM.from_pretrained("Yooniii/Article_summarizer")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    inputs = tokenizer.encode(article, return_tensors="pt", max_length=1024, truncation=True).to(device)
    summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Function to save content to a text file
def save_to_file(filename, title, original_content, summary, sentiment):
    wrapper = textwrap.TextWrapper(width=80)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n\n")
        f.write("Original Content:\n")
        original_wrapped = wrapper.fill(original_content)
        f.write(original_wrapped + "\n\n")
        f.write("Summary:\n")
        summary_wrapped = wrapper.fill(summary)
        f.write(summary_wrapped + "\n\n")
        f.write(f"Predicted Sentiment: {sentiment}\n")
