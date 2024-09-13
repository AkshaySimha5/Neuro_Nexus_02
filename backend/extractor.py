# -*- coding: utf-8 -*-
import re
import copy
import requests
from bs4 import BeautifulSoup, Comment, NavigableString
import html2text

class Extractor():
    def __init__(self, url, html, threshold, output, **kwargs):
        self.url = url
        self.title = ''
        self.html = html
        self.output = output
        self.threshold = threshold
        self.kwargs = kwargs
        if not self.html:
            self.html = self.__download()

    def __process_text_ratio(self, soup) -> tuple:
        """ Calculate the ratio of text vs. HTML tags for a given soup element """
        soup = copy.copy(soup)
        if soup:
            if isinstance(soup, NavigableString):
                return 1
            for t in soup.find_all(['script', 'style', 'noscript', 'a', 'img']):
                t.extract()
            soup_str = re.sub(
                r'\s*[^=\s+]+\s*=\s*([^=>]+)?(?=(\s+|>))', "", str(soup))
            total_len = len(soup_str)
            if total_len:
                tag_len = 0.0
                for tag in re.compile(r'</?\w+[^>]*>|[\s]', re.S).findall(soup_str):
                    tag_len += len(tag)
                return (total_len - tag_len) / total_len, total_len
        return 0, 0

    def __find_article_html(self, soup) -> BeautifulSoup:
        """ Find the main content by looking for article-related tags and excluding unwanted sections. """
        if not soup:
            return None
        if isinstance(soup, NavigableString):
            return soup

        # Remove unwanted elements such as ads and recommendations
        unwanted_selectors = [
            {'tag': 'div', 'class_': re.compile(r'ad|ads|sponsored|promo|related|recommendation|footer')},  # Common ad classes
            {'tag': 'aside'},  # <aside> often contains ads or side content
            {'tag': 'nav'},  # <nav> is for navigation, which we don’t need
            {'tag': 'footer'},  # Footer is not part of the main article
            {'tag': 'section', 'class_': re.compile(r'related|recommendations')},  # Sections for related content
        ]
        
        for selector in unwanted_selectors:
            if 'class_' in selector:
                for unwanted_tag in soup.find_all(selector['tag'], class_=selector['class_']):
                    unwanted_tag.extract()  # Remove the unwanted tag
            else:
                for unwanted_tag in soup.find_all(selector['tag']):
                    unwanted_tag.extract()  # Remove the unwanted tag

        # Common classes or tags that hold article content on news websites
        article_selectors = [
            {'tag': 'article'},  # Many news sites use <article> tag for news content
            {'tag': 'div', 'class_': re.compile(r'article|content|main|story')},  # Matching common article classes
            {'tag': 'section', 'class_': re.compile(r'article|content|main|story')},  # Sometimes sections are used
        ]

        for selector in article_selectors:
            # Find potential article content tags
            if 'class_' in selector:
                article_tag = soup.find(selector['tag'], class_=selector['class_'])
            else:
                article_tag = soup.find(selector['tag'])

            if article_tag:
                # If a matching tag is found, return that tag as the article content
                return article_tag

        # If no specific article tags are found, use the default ratio-based logic
        return self.__find_largest_text_block(soup)

    def __find_largest_text_block(self, soup) -> BeautifulSoup:
        """ Fallback: Find the largest text block based on text-to-HTML ratio. """
        article_content = []
        parent_radio = self.__process_text_ratio(soup)[0]

        for tag in soup.find_all(['p', 'div']):
            # Calculate the text ratio of each tag
            tag_radio, tag_len = self.__process_text_ratio(tag)
            if tag_len > 0 and tag_radio >= parent_radio:
                # Accumulate potential article content based on the text ratio threshold
                article_content.append(tag)

        # If significant tags found, return the combined result as one soup
        if article_content:
            return BeautifulSoup(" ".join([str(tag) for tag in article_content]), 'lxml')
        return soup

    def __get_title(self, soup) -> str:
        """ Extract the article title based on h1-h6 tags or <title> """
        title = ''
        if soup:
            for t in soup.find_all_previous(re.compile("^h[1-6]")):
                if t.text:
                    title = t.text
                    break

        if not title:
            html = BeautifulSoup(self.html, 'lxml')
            if html.title:
                title = html.title.text.split('_')[0].split('|')[0]

        self.title = re.sub(r'<[\s\S]*?>|[\t\r\f\v]|^\s+|\s+$', "", title)
        return self.title

    def __download(self) -> str:
        """ Download HTML content from the given URL """
        response = requests.get(self.url, **self.kwargs)
        response.raise_for_status()
        html = ''
        if response.encoding != 'ISO-8859-1':
            # return response as a unicode string
            html = response.text
        else:
            html = response.content
            if 'charset' not in response.headers.get('content-type'):
                encodings = requests.utils.get_encodings_from_content(response.text)
                if len(encodings) > 0:
                    response.encoding = encodings[0]
                    html = response.text
        return html

    def parse(self) -> tuple:
        """ Parse the HTML and extract the article """
        soup = BeautifulSoup(self.html, 'lxml').find('body')
        if soup:
            for tag in soup.find_all(style=re.compile('display:\s?none')):
                tag.extract()
            for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
                comment.extract()

            article_html = self.__find_article_html(soup)
            if self.output == 'markdown':
                return self.__get_title(article_html), self.__html_to_md(article_html)
            else:
                return self.__get_title(article_html), self.__clean_html(article_html)
        return '', ''

    def __html_to_md(self, soup) -> str:
        """ Convert HTML to Markdown """
        return html2text.html2text(str(soup), baseurl=self.url)

    def __clean_html(self, soup) -> str:
        """ Extract only text from HTML, remove unwanted tags """
        text_content = BeautifulSoup(str(soup), 'lxml').get_text(separator=' ', strip=True)
        return text_content


# Utility function to use the Extractor class
def parse(url='', html='', threshold=0.9, output='html', **kwargs):
    """
    Extract article by URL or HTML.

    :param url: URL for the article.
    :param html: HTML for the article.
    :param threshold: The ratio of text to the entire document, default 0.9.
    :param output: Result output format, supports ``markdown`` and ``html``, default ``html``.
    :param **kwargs: Optional arguments that ``requests.get`` takes.
    :return: :class:`tuple` object containing (title, article_content)
    """
    ext = Extractor(url=url, html=html, threshold=threshold, output=output, **kwargs)
    return ext.parse()


# Example usage
if __name__ == "__main__":
    # Replace 'your_news_article_url_here' with the actual news article URL
    url = 'https://www.bbc.com/news/articles/clywepq2eq2o'
    
    # Call the parse function with the URL
    title, content = parse(url=url)
    
    # Print the extracted title and content
    print("Title:", title)
    print("Content:", content)