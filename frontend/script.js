const API_KEY = "d833e5a2152f409694454d01cd16171e";
const url = "https://newsapi.org/v2/everything?q=";

// URL of your Flask server
const backendUrl = "http://127.0.0.1:5000/fetch_article"; // Adjust if needed

window.addEventListener("load", () => fetchNews("India"));

function reload() {
    window.location.reload();
}

async function fetchNews(query) {
    const res = await fetch(`${url}${query}&apiKey=${API_KEY}`);
    const data = await res.json();
    bindData(data.articles);
}

function bindData(articles) {
    const cardsContainer = document.getElementById("cards-container");
    const newsCardTemplate = document.getElementById("template-news-card");

    cardsContainer.innerHTML = "";

    articles.forEach((article) => {
        if (!article.urlToImage) return;
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

    newsImg.addEventListener("click", () => {
        openArticleInNewTab(article.url);
    });
}

async function openArticleInNewTab(url) {
    try {
        // Fetch the article summary and title
        const res = await fetch(`${backendUrl}?url=${encodeURIComponent(url)}`);
        const data = await res.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const { title, summary, category } = data;

        // Open a new window or tab
        const newWindow = window.open("", "_blank");

        // Check if the window was successfully created
        if (!newWindow) {
            console.error("Popup blocked or failed to open a new window");
            alert("Please allow popups for this website.");
            return;
        }

        // Write the article details to the new window
        newWindow.document.write(`
            <html>
            <head>
                <title>${title}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { font-size: 24px; }
                    p { font-size: 18px; line-height: 1.6; }
                </style>
            </head>
            <body>
                <h1>${title}</h1>
                <p>${summary}</p>
                <h1>${category}</h1>
            </body>
            </html>
        `);

        // Close the document stream so that it loads correctly
        newWindow.document.close();
    } catch (error) {
        console.error("Error fetching article content:", error);
    }
}



async function fetchArticleContent(url) {
    try {
        // Fetch the title and summary instead of content
        const res = await fetch(`${backendUrl}?url=${encodeURIComponent(url)}`);
        const data = await res.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        showArticleDetails(data.title, data.summary
        );
    } catch (error) {
        console.error("Error fetching article content:", error);
    }
}

function showArticleDetails(title, summary) {
    const displaySection = document.getElementById("news-display");
    const displayTitle = document.getElementById("display-title");
    const displayContent = document.getElementById("display-content");

    // Set title and summary (not content)
    displayTitle.textContent = title;
    displayContent.textContent = summary;

    displaySection.style.display = "block";
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
