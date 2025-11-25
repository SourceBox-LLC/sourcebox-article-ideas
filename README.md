# SourceBox Article Drafter

Automated article idea drafter that analyzes existing articles from SourceBox AI's blog and generates new article ideas and drafts.

## Features

- Fetches existing articles from sourceboxai.com/blog
- Analyzes articles to identify common themes and topics
- Generates new article ideas based on existing content
- Creates full article drafts using AI
- Saves drafts to JSON file for review

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your REPLICATE_API_TOKEN
```

## Usage

Run the article drafter:
```bash
python main.py
```

The script will:
1. Fetch all articles from the SourceBox blog
2. Analyze them for themes and topics
3. Generate new article ideas (default: 3)
4. Create full drafts for each idea
5. Save drafts to `article_drafts.json`

## Configuration

Set the number of article ideas to generate:
```bash
# In .env file
NUM_IDEAS=5
```

## Output

Drafts are saved to `article_drafts.json` with the following structure:
```json
[
  {
    "title": "Article Title",
    "description": "Brief description",
    "content": "Full article in Markdown format",
    "generated_at": "2025-11-24T..."
  }
]
```
