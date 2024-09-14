const API_KEY = "d833e5a2152f409694454d01cd16171e";
const url = "https://newsapi.org/v2/everything?q=";

// URL of your Flask server
const backendUrl = "http://127.0.0.1:5000/fetch_article"; // Adjust if needed

window.addEventListener("load", () => fetchNews("India"));

function reload() {
    window.location.reload();
}

async function fetchNews(query) {
    try {
        const res = await fetch(`${url}${query}&apiKey=${API_KEY}`);
        if (!res.ok) {
            throw new Error("Failed to fetch news articles");
        }
        const data = await res.json();
        bindData(data.articles);
    } catch (error) {
        console.error("Error fetching news:", error);
        alert("Failed to load news articles. Please try again later.");
    }
}

function bindData(articles) {
    const cardsContainer = document.getElementById("cards-container");
    const newsCardTemplate = document.getElementById("template-news-card");

    cardsContainer.innerHTML = ""; // Clear existing cards

    articles.forEach((article) => {
        if (!article.urlToImage) return; // Skip articles without images
        const cardClone = newsCardTemplate.content.cloneNode(true);
        fillDataInCard(cardClone, article);
        cardsContainer.appendChild(cardClone);
    });
}

function fillDataInCard(cardClone, article) {
    const newsImg = cardClone.querySelector("#news-img");
    const newsTitle = cardClone.querySelector("#news-title");
    const newsSource = cardClone.querySelector("#news-source");
    const newsDesc = cardClone.querySelector("#news-desc");

    newsImg.src = article.urlToImage;
    newsTitle.innerHTML = article.title;
    newsDesc.innerHTML = article.description;

    const date = new Date(article.publishedAt).toLocaleString("en-US", {
        timeZone: "Asia/Jakarta",
    });
    newsSource.innerHTML = `${article.source.name} · ${date}`;

    // Add event listener to open article in a new tab
    newsImg.addEventListener("click", () => {
        openArticleInNewTab(article.url);
    });
}

async function openArticleInNewTab(url) {
    try {
        // Fetch the article summary, category, and sentiment from the backend
        const res = await fetch(`${backendUrl}?url=${encodeURIComponent(url)}`);
        const data = await res.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const { title, summary, category, sentiment } = data;

        // Open a new window or tab for the article details
        const newWindow = window.open("", "_blank");

        // Check if the new window was successfully opened
        if (!newWindow) {
            console.error("Popup blocked or failed to open a new window");
            alert("Please allow popups for this website.");
            return;
        }

        // Write article details (title, summary, category, and sentiment) to the new window
        newWindow.document.write(`
           <html>
<head>
    <title>${title}</title>
    <link  rel="stylesheet" href="index.css">
    <style>
        /* Applying background color and fonts similar to first HTML */
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5; /* Light background color */
            color: #333; /* Text color */
        }

        /* Styling for headings */
        h1 { 
            font-size: 32px; 
            font-family: 'Oswald', sans-serif;
            color: #2c3e50; /* Darker heading color */
        }

        /* Paragraph styling */
        p { 
            font-size: 18px; 
            line-height: 1.6; 
            color: #444;
        }

        /* Styling for the logo at the top */
     

        

        /* Link styling inside the nav */
       
    </style>
</head>
<body>

    <!-- Added the logo from first HTML -->
    <nav>
        <img src="logo.jpg" alt="Logo" class="logo">
        <ul>
            <li><a href="index.html">HOME</a></li>
            <li><a href="summarize.html" target="_blank">TRY HERE</a></li>
        </ul>
    </nav>

    <br/>
    <!-- Content from second HTML -->
    <h1>${title}</h1>
    <p><strong>Summary:</strong> ${summary}</p>
    <p><strong>Category:</strong> ${category}</p>
    <p><strong>Sentiment:</strong> ${sentiment}</p>
</body>
</html>

        `);

        // Close the document stream so that it renders correctly
        newWindow.document.close();
    } catch (error) {
        console.error("Error fetching article content:", error);
    }
}

let curSelectedNav = null;

function onNavItemClick(id) {
    fetchNews(id);
    const navItem = document.getElementById(id);
    if (curSelectedNav) {
        curSelectedNav.classList.remove("active");
    }
    curSelectedNav = navItem;
    curSelectedNav.classList.add("active");
}

const searchButton = document.getElementById("search-button");
const searchText = document.getElementById("search-text");

searchButton.addEventListener("click", () => {
    const query = searchText.value;
    if (!query) return;
    fetchNews(query);
    if (curSelectedNav) {
        curSelectedNav.classList.remove("active");
    }
    curSelectedNav = null;
});

function openCategoryPage(category) {
    // Open a new page and pass the selected category as a query parameter
    const url = `news.html?category=${category}`;
    window.open(url, '_blank');
}
