#!/usr/bin/env python3
import json
import logging
from urllib.parse import urljoin
import time
import random
import urllib.robotparser
import requests
from bs4 import BeautifulSoup
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

BASE_URL = "https://www.borgwarner.com"
PRESS_RELEASES_URL = f"{BASE_URL}/newsroom/press-releases"
ROBOTS_URL = f"{BASE_URL}/robots.txt"
JSON_FILE_PATH = "borgwarner_press_releases.json"
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2", 
    model_kwargs={"device": "cpu"}
)
vector_db = Chroma(
    embedding_function=embedding_model, 
    persist_directory="./chroma_db"
)


def is_scraping_allowed():
    """
    Checks if scraping is allowed by robots.txt.
    """
    try:
        response = requests.get(ROBOTS_URL, timeout=10, verify=True)
        response.raise_for_status()
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(response.text.splitlines())
        allowed = rp.can_fetch("*", PRESS_RELEASES_URL)
        return allowed

    except requests.exceptions.SSLError:
        logging.error("SSL Certificate verification failed. Retrying without verification...")
        try:
            response = requests.get(ROBOTS_URL, timeout=10, verify=False)
            response.raise_for_status()
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(response.text.splitlines())
            return rp.can_fetch("*", PRESS_RELEASES_URL)
        except Exception as e:
            logging.error(f"Error retrieving robots.txt: {e}")
            return False 

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            logging.warning("robots.txt not found (404). Assuming scraping is allowed.")
            return True  # Assuming No robots.txt means no restrictions.
        logging.error(f"HTTP error while checking robots.txt: {e}")
        return False

    except Exception as e:
        logging.error(f"Error checking robots.txt: {e}")
        return False


def get_embedding(text):
    """
    Convert text into vector embeddings.
    """
    return embedding_model.embed_query(text)


def store_in_vector_db(title, publication_date, content_url, content):
    """
    Store press release data in the vector database.
    """
    existing_docs = vector_db.get(where={"url": content_url})
    if existing_docs["documents"]:
        logging.debug(f"Skipping: Document '{title}' for url: {content_url} already exists.")
        return
    doc = Document(
        page_content=content,
        metadata={"title": title, "date": publication_date, "url": content_url}
    )
    vector_db.add_documents([doc])
    logging.info(f"Successfully Added Document for Title: {title}, Publication Date: {publication_date}")


def query_knowledge_base(query_text, top_k=5):
    """
    Finds the most relevant press releases for a query.
    """
    results = vector_db.similarity_search_with_score(query_text, k=top_k)

    if not results:
        print("No relevant results found.")
        return []
    
    return [
        {
            "title": res.metadata["title"],
            "date": res.metadata["date"],
            "url": res.metadata["url"],
            "score": round(score,2)
        }
        for res, score in results
    ]


def get_press_release_contents(page_url):
    """
    Fetches a press release listing page and returns a list of full URLs
    for each press release found on that page.
    """
    try:
        response = session.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        contents = []
        press_releases = soup.select("div.column.widget-block")
        if not press_releases:
            logging.warning("No press release blocks found! The website structure might have changed.")
            return contents
        for article in press_releases:
            title_tag = article.select_one("h2.bw-global-list-h3")
            if title_tag:
                title = title_tag.get_text(strip=True).replace("\r", "")
            else:
                title = None
                logging.warning("Title Not found! The website structure might have changed.")

            date_tag = article.select_one("div.h5.margin-bottom-0")
            if date_tag:
                publication_date = date_tag.get_text(strip=True)
            else:
                publication_date = None
                logging.warning("Publication date Not found! The website structure might have changed.")

            a_tag = title_tag.select_one("a") if title_tag else None
            if a_tag and a_tag.get("href"):
                content_url = urljoin(BASE_URL, a_tag["href"])
            else:
                logging.warning("Content URL Not found! The website structure might have changed.")
                content_url = None

            content = parse_press_release_content(content_url) if content_url else None

            if content:
                store_in_vector_db(title, publication_date, content_url, content)

            if content and (not any(article["content_url"] == content_url for article in contents)):
                contents.append({
                    "publication_date": publication_date,
                    "title": title,
                    "content_url": content_url,
                    "content": content
                })
                
        return contents
    except Exception as e:
        logging.error(f"Error fetching press release links from {page_url}: {e}")
        return []


def parse_press_release_content(article_url):
    """
    Given a press release URL, fetches and extracts the full text content of the article.
    """
    try:
        response = session.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find("div", class_="sfnewsContent sfcontent")
        if content_div:
            content_text = " ".join(content_div.stripped_strings).replace("\n", "").replace("\r", "")
        else:
            content_text = None
            logging.warning(f"Content Not found on url: {article_url}! The website structure might have changed.")
        
        return content_text
    except Exception as e:
        logging.error(f"Error parsing article {article_url}: {e}")
        return None


def query_cli():
    """
    Command-line interface for querying the knowledge base.
    """
    print("\n🔍 Press Release Search")
    print("Type your query or type 'exit' to quit.")

    while True:
        query_text = input("\nEnter your query: ").strip()
        if query_text.lower() == "exit":
            print("Goodbye! 👋")
            break

        if not query_text:
            print("Please Enter your query! You have not provided Anything")
            continue

        results = query_knowledge_base(query_text)
        if results:
            print("\n🔹 Top 5 Matching Press Releases:")
            for idx, result in enumerate(results, 1):
                print(
                    f"{idx}. {result['title']} ({result['date']}) "
                    f"Matched with Score: {result['score']}\n"
                    f"   🔗 {result['url']}\n"
                )
        else:
            print("❌ No relevant results found.")


def main():
    articles = []
    current_page = 1
    max_page = 10
    while current_page <= max_page:
        page_url = f"{PRESS_RELEASES_URL}/Page/{current_page}/all/all/all/all/all/all"
        logging.info(f"Fetching press release listing: {page_url}")
        contents = get_press_release_contents(page_url)
        if not contents:
            logging.warning(f"No press releases found for page: {current_page}, Stopping!")
            break
        
        articles.extend(contents)
        current_page += 1
        
        time.sleep(random.uniform(1, 3))
    
    try:
        with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        logging.info(f"Scraping complete. Data saved to {JSON_FILE_PATH} and Vector DB")
    except Exception as e:
        logging.error(f"Error saving data to {JSON_FILE_PATH}: {e}")


if __name__ == "__main__":
    if not is_scraping_allowed():
        logging.error("Scraping not allowed by robots.txt")
        exit()
    session = requests.Session()
    main()
    query_cli()

