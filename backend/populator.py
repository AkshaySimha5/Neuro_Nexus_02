import requests

# Replace with your actual API key
api_key = "9f767a279d474e299017270ffdd2e001"

# List of categories to fetch news from
categories = ['sports', 'politics', 'business', 'technology']

# Iterate through each category
for category in categories:
    print(f"\nNews for Category: {category.capitalize()}\n" + "-"*40)
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={api_key}"
    
    # Make the request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        news_data = response.json()
        # Print the titles and URLs of the news articles
        if 'articles' in news_data and news_data['articles']:
            for article in news_data['articles']:
                print(f"Title: {article['title']}")
                print(f"URL: {article['url']}")
                print()  # Print a blank line between articles
        else:
            print(f"No articles found for category: {category}")
    else:
        print(f"Error fetching {category} news: {response.status_code}")
    
    # Add a line break between categories
    print("\n")