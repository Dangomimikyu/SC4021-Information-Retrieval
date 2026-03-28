# SC4021-Information-Retrieval
AY 25/26 Sem 2, SC4021 Information Retrieval
          
# ⚽ Football Sentiment Analysis Platform

A comprehensive search engine and sentiment analysis tool for football-related discussions, built with **Apache Solr**, **React**, and **Node.js**.

## 🔍 About The Project
This project was developed for the **SC4021 Information Retrieval** course. It provides a powerful interface to search through thousands of indexed Reddit football posts and comments. Beyond simple keyword matching, the platform performs real-time sentiment analysis to visualize the "mood" of the football community.

---

## ✨ Key Features
* **Multi-Field Search**: Query data by title, content, author, or subreddit.
* **Sentiment Breakdown**: Automatic classification of comments into Positive, Negative, and Neutral.
* **Smart Data Parsing**: Custom Python-list parser for complex nested Reddit comments.
* **Interactive Visualization**: Real-time sentiment charts for both global results and individual posts.
* **Expandable UI**: Clean layout with toggleable comment sections and smooth transitions.

---

## 🛠 Tech Stack
* **Frontend**: React.js 18 (TypeScript), Tailwind CSS, Recharts.
* **Backend**: Node.js (Express), TypeScript, Axios.
* **Search Engine**: Apache Solr 9.x.
* **Infrastructure**: Docker & Docker Compose.

---

## 🚀 Getting Started

### Prerequisites
Make sure you have **Docker Desktop** installed on your system:
* [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Installation

1. **Clone the repository**
```bash
git clone [https://github.com/Dangomimikyu/SC4021-Information-Retrieval.git](https://github.com/Dangomimikyu/SC4021-Information-Retrieval.git)
```
2. **Navigate to the project directory**
```bashcd SC4021-Information-Retrieval
```
3. **Build and run the containers**
```
docker-compose up --build

