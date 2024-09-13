document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const category = urlParams.get('category');
  const api_key = "9f767a279d474e299017270ffdd2e001"; // Replace with your API key
  const newsContainer = document.getElementById('news-cards-container');
  
  // Fetch news for the selected category
  fetch(`https://newsapi.org/v2/top-headlines?category=${category}&apiKey=${api_key}`)
      .then(response => response.json())
      .then(data => {
          if (data.articles && data.articles.length > 0) {
              data.articles.forEach(article => {
                  // Create a news card for each article
                  const newsCard = document.createElement('div');
                  newsCard.classList.add('card');
                  
                  newsCard.innerHTML = `
                      <div class="card-header">
                          <img src="${article.urlToImage || 'https://via.placeholder.com/400x200'}" alt="news-image">
                      </div>
                      <div class="card-content">
                          <h3>${article.title}</h3>
                          <h6 class="news-source">${article.source.name} ${new Date(article.publishedAt).toLocaleDateString()}</h6>
                          <p class="news-desc">${article.description || 'Description not available'}</p>
                          <a href="${article.url}" target="_blank">Read More</a>
                      </div>
                  `;
                  
                  // Append the news card to the container
                  newsContainer.appendChild(newsCard);
              });
          } else {
              newsContainer.innerHTML = '<p>No news articles available for this category.</p>';
          }
      })
      .catch(error => console.error('Error fetching news:', error));
});
