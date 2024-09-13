document.getElementById('summarize-btn').addEventListener('click', async function () {
  const url = document.getElementById('url-input').value;
  const backendUrl = 'http://127.0.0.1:5000/fetch_article'; // Replace with your backend URL

  try {
      // Fetch the article summary and title
      const res = await fetch(`${backendUrl}?url=${encodeURIComponent(url)}`);
      const data = await res.json();

      if (data.error) {
          console.error(data.error);
          alert('Error fetching summary: ' + data.error);
          return;
      }

      const { title, summary, category } = data;

      // Populate the content in the summary section
      document.getElementById('article-title').textContent = title;
      document.getElementById('article-summary').textContent = summary;
      document.getElementById('article-category').textContent = `Category: ${category}`;

      // Show the summary section
      document.getElementById('summary-section').style.display = 'block';

  } catch (error) {
      console.error('Error fetching the article summary:', error);
      alert('Failed to fetch the summary.');
  }
});
