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

## Work Flow of the Scraper

1. **Check if Scraping is Allowed**
   The script first verifies the `robots.txt` file to ensure scraping is permitted.

2. **Start Scraping**
   The script scrapes all articles of First 10 pages
   - Content of Each article is indexed into a vector database (ChromaDB) for querying.
   - It is also stored in `borgwarner_press_releases.json` for debugging and visualization purposes.
   
   After the scraping is complete, you can interactively search for press releases:
   - The CLI will prompt you to enter a query.

   ```
    🔍 Press Release Search
    Type your query or type 'exit' to quit.

    Enter your query:
   ```
   - The script retrieves the top matching press releases based on semantic similarity.

    ```
    Enter your query: BorgWarner Announces CFO Succession Plan

    🔹 Top 5 Matching Press Releases:
    1. BorgWarner Announces CFO Succession Plan (Dec 05, 2023) Matched with Score: 0.7
       🔗 https://www.borgwarner.com/newsroom/press-releases/2023/12/05/borgwarner-announces-cfo-succession-plan
    
    2. BorgWarner Announces CEO Succession Plan (Nov 07, 2024) Matched with Score: 0.7
       🔗 https://www.borgwarner.com/newsroom/press-releases/2024/11/07/borgwarner-announces-ceo-succession-plan
    
    3. BorgWarner Announces Appointment of Joseph Fadool as Chief Operating Officer (May 30, 2024) Matched with Score: 0.75
       🔗 https://www.borgwarner.com/newsroom/press-releases/2024/05/30/borgwarner-announces-appointment-of-joseph-fadool-as-chief-operating-officer
    
    4. BorgWarner Declares Quarterly Dividend (Feb 10, 2022) Matched with Score: 0.84
       🔗 https://www.borgwarner.com/newsroom/press-releases/2022/02/10/borgwarner-declares-quarterly-dividend
    
    5. BorgWarner Named in U.S. News & World Report’s 2023-2024 Best Companies to Work For (Jul 06, 2023) Matched with Score: 0.87
       🔗 https://www.borgwarner.com/newsroom/press-releases/2023/07/06/borgwarner-named-in-u.s.-news---world-report-s-2023-2024-best-companies-to-work-for

    ```
   - To Exit the process please enter "exit" in Query
     ```
     Enter your query: exit
     Goodbye! 👋
     ```

## Assumptions
- The website structure remains consistent (if it changes, parsing logic may break).
- The scraper follows all ethical guidelines and obeys `robots.txt` rules.

## Limitations
- The scraper may fail if the website changes its layout.
- The knowledge base search relies on the quality of vector embeddings.
