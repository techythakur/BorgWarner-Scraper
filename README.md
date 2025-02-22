# BorgWarner Press Release Scraper & Knowledge Base

This project is a web scraper for BorgWarner press releases (https://www.borgwarner.com/newsroom/press-releases), which stores extracted data in a vector database i.e. ChromaDB for efficient querying using Text embeddings.

## Features
- Scrapes BorgWarner press releases
- Stores data in a vector database (ChromaDB) and in a JSON file (only for debugging and visualization purposes) 
- Uses Langchain's sentence-transformers for text embedding
- Provides a command-line interface for querying the knowledge base

## Installation and Setup

### 1. Clone the Repository
```sh
git clone https://github.com/techythakur/BorgWarner-Scraper.git
cd BorgWarner-Scraper
```

### 2. Create a Virtual Environment
```sh
python3 -m venv scraper
source scraper/bin/activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Run the Scraper
```sh
python3 borgwarner_scraper.py
```

After the scraping is done, please go ahead and enter your queries into the CLI. It will return the Top 5 Most relevant articles with a Score (#note: Articles with score closest to 0 are the most relevant)

## Dependencies
- `requests`
- `beautifulsoup4`
- `langchain`
- `langchain_chroma`
- `langchain_huggingface`
