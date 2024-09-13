import requests

# Replace with your actual API key
api_key = "9f767a279d474e299017270ffdd2e001"

# List of categories to fetch news from
categories = ['sports', 'politics', 'business', 'technology']

# Replace with your actual API endpoint
post_url = "https://your-endpoint.com/api/news"

# Iterate through each category
for category in categories:
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={api_key}"
    
    # Make the request to fetch news
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        news_data = response.json()
        
        # If articles exist, prepare the payload
        if 'articles' in news_data and news_data['articles']:
            for article in news_data['articles']:
                # Create the payload with title and URL
                payload = {
                    "title": article['title'],
                    "url": article['url'],
                    "category": category
                }
                
                # Send the payload via POST request
                post_response = requests.post(post_url, json=payload)
                
                # Check if the POST request was successful
                if post_response.status_code == 200:
                    print(f"Successfully sent news: {article['title']}")
                else:
                    print(f"Error sending news: {post_response.status_code}")
        else:
            print(f"No articles found for category: {category}")
    else:
        print(f"Error fetching {category} news: {response.status_code}")
    
    # Add a line break between categories
    print("\n")
