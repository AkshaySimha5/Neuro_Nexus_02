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
        const res = await fetch(`${backendUrl}?url=${encodeURIComponent(url)}`);
        const data = await res.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const { title, content } = data;
        const newWindow = window.open("", "_blank");
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
                <p>${content}</p>
            </body>
            </html>
        `);
        newWindow.document.close();
    } catch (error) {
        console.error("Error fetching article content:", error);
    }
}

async function fetchArticleContent(url) {
    try {
        const res = await fetch(`${backendUrl}?url=${encodeURIComponent(url)}`);
        const data = await res.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        showArticleDetails(data.title, data.content);
    } catch (error) {
        console.error("Error fetching article content:", error);
    }
}

function showArticleDetails(title, content) {
    const displaySection = document.getElementById("news-display");
    const displayTitle = document.getElementById("display-title");
    const displayContent = document.getElementById("display-content");

    displayTitle.textContent = title;
    displayContent.textContent = content;

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
