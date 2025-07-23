# Paragon University AI Chatbot

Intelligent Telegram chatbot providing automated responses about Paragon International University using web scraping, vector search, and LLM integration.

## Architecture Overview

```
Telegram Message → n8n Workflow → FastAPI Backend → FAISS Search → LLM Response → Telegram
```

## System Components

### 1. **Web Scraper** (`paragon_scraper/`)
- Scrapy-based crawler for university website content
- Extracts structured data about programs, admissions, facilities
- Outputs JSONL format for processing

### 2. **Vector Search Engine** (`create_faiss_index.py`, `faiss_index/`)
- Creates FAISS index from scraped content
- Enables semantic search using embeddings
- Fast similarity matching for relevant content retrieval

### 3. **FastAPI Backend** (`app.py`)
- REST API endpoint for search queries
- Integrates FAISS index with query processing
- Returns ranked results with relevance scores

### 4. **n8n Automation Workflow** (`Telegram_ParagonBot.json`)
- Orchestrates entire chatbot pipeline
- Handles Telegram webhook integration
- Manages question validation and response routing

## Features

- **Smart Question Filtering**: Only responds to university-related queries
- **Semantic Search**: Finds relevant content using vector similarity
- **Answer Validation**: Ensures responses contain actual university information
- **Graceful Fallbacks**: Helpful messages when information isn't available
- **Source Citations**: Links back to original university pages

## Installation & Setup

### Prerequisites
```bash
pip install -r requirements.txt
```

### 1. Run Web Scraper
```bash
cd paragon_scraper
scrapy crawl paragon_spider -o paragon_data.jsonl
```

### 2. Create Search Index
```bash
python create_faiss_index.py
```

### 3. Start FastAPI Backend
```bash
python app.py
```

### 4. Import n8n Workflow
1. Open n8n interface
2. Import `Telegram_ParagonBot.json`
3. Configure Telegram bot credentials
4. Set OpenRouter API credentials
5. Update FastAPI endpoint URL

### 5. Configure Telegram Bot
1. Create bot via @BotFather on Telegram
2. Get bot token and add to n8n credentials
3. Set webhook URL in n8n Telegram trigger

## Project Structure

```
paragonai/
├── README.md
├── requirements.txt
├── app.py                          # FastAPI backend
├── create_faiss_index.py          # Index creation script
├── Telegram_ParagonBot.json       # n8n workflow
├── paragon_scraper/               # Scrapy project
│   ├── scrapy.cfg
│   ├── paragon_scraper/
│   │   ├── __init__.py
│   │   ├── items.py
│   │   ├── middlewares.py
│   │   ├── pipelines.py
│   │   ├── settings.py
│   │   └── spiders/
│   └── paragon_data.jsonl         # Scraped data
├── faiss_index/                   # Generated search index
│   ├── faiss_index.bin
│   └── metadata.pkl
└── venv/                          # Virtual environment (exclude from git)
```

## Workflow Logic

### Question Processing Pipeline:
1. **Telegram Trigger** - Receives user message
2. **Question Validator** - Checks if query is university-related
3. **Relevance Check** - Routes to appropriate response
4. **HTTP Request** - Queries FastAPI backend if relevant
5. **Answer Question** - Generates response using LLM + context
6. **Answer Validator** - Verifies response quality
7. **Response Routing** - Sends appropriate message to user

### Response Types:
- **Valid Answer**: Direct response with source citation
- **Off-Topic**: Friendly redirect to university topics
- **No Information**: Helpful message suggesting query refinement

## Configuration

### n8n Workflow Settings:
- **LLM Model**: `deepseek/deepseek-r1-0528:free`
- **Search Results**: Top 5 most relevant chunks
- **Question Validation**: University topic filtering
- **Answer Validation**: Response quality checking

### FastAPI Backend:
- **Endpoint**: `/search`
- **Method**: POST
- **Payload**: `{"query_text": "user question", "k": 5}`
- **Response**: Ranked search results with scores

## API Endpoints

### POST `/search`
Search university content for relevant information.

**Request:**
```json
{
  "query_text": "What programs does Paragon offer?",
  "k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "Paragon offers programs in...",
      "score": 0.95,
      "url": "https://paragon.edu.kh/programs"
    }
  ]
}
```

## Required Credentials

1. **Telegram Bot Token** - From @BotFather
2. **OpenRouter API Key** - For LLM responses
3. **n8n Instance** - For workflow automation

## Development Notes

- Uses Scrapy for robust web scraping
- FAISS provides efficient similarity search
- n8n enables visual workflow automation
- FastAPI offers high-performance API backend
- Modular design allows independent component updates

## Deployment Considerations

- Run FastAPI backend on accessible server
- Configure n8n with proper webhook URLs
- Ensure FAISS index is accessible to API
- Set up monitoring for scraper updates
- Consider rate limiting for API endpoints

## License

Open source - modify as needed for your use case.
