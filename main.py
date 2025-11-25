import json
import os
from datetime import datetime

from helpers.get_articles import fetch_all_articles
from helpers.models import run_text_model
from helpers.notion_client import create_notion_page_for_draft


def analyze_existing_articles(articles):
    """Analyze existing articles to understand topics and themes."""
    print("\nAnalyzing existing articles for themes and topics...")

    # Create a summary of existing articles
    article_summaries = []
    for article in articles[:10]:  # Analyze first 10 articles for efficiency
        article_summaries.append(f"Title: {article['title']}")

    summaries_text = "\n".join(article_summaries)

    prompt = f"""You are analyzing blog articles from SourceBox AI, a company that provides AI-powered tools.

Below are titles from recent blog articles:

{summaries_text}

Based on these articles, what are the main themes and topics covered? List 3-5 key themes.
Keep it concise - just list the themes, one per line."""

    themes = run_text_model(prompt)
    print("\nIdentified themes:")
    print(themes)
    return themes


def generate_article_ideas(themes, num_ideas=3):
    """Generate new article ideas based on identified themes."""
    print(f"\nGenerating {num_ideas} new article ideas...")

    prompt = f"""You are a content strategist for SourceBox AI, a company that provides AI-powered tools.

Based on these existing themes from our blog:
{themes}

Generate {num_ideas} new, fresh article ideas that would be valuable to our audience.

For each idea, provide:
1. A compelling title (engaging and specific)
2. A brief description (2-3 sentences about what the article would cover)

Format your response as a JSON array like this:
[
  {{
    "title": "Article title here",
    "description": "Article description here"
  }}
]

Just return the JSON array, nothing else."""

    response = run_text_model(prompt)

    # Try to parse JSON from the response
    try:
        # Sometimes models wrap JSON in markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()

        ideas = json.loads(response)
        return ideas
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response was: {response}")
        return []


def generate_article_draft(idea):
    """Generate a full draft for a given article idea."""
    print(f"\nGenerating draft for: {idea['title']}")

    prompt = f"""You are a technical content writer for SourceBox AI.

Write a complete blog article with the following details:

Title: {idea['title']}
Brief: {idea['description']}

Requirements:
- Write in an informative, professional tone
- Include an engaging introduction
- Use clear section headings
- Provide practical insights and examples
- Conclude with actionable takeaways
- Aim for 800-1200 words

Write the article in Markdown format."""

    draft = run_text_model(prompt)
    return draft


def save_drafts(drafts, filename="article_drafts.json"):
    """Save article drafts to a JSON file."""
    output_path = os.path.join(os.path.dirname(__file__), filename)

    # Load existing drafts if file exists
    existing_drafts = []
    if os.path.exists(output_path):
        try:
            with open(output_path, "r") as f:
                existing_drafts = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load existing drafts: {e}")

    # Add timestamp to new drafts
    timestamp = datetime.now().isoformat()
    for draft in drafts:
        draft["generated_at"] = timestamp

    # Combine and save
    all_drafts = existing_drafts + drafts

    with open(output_path, "w") as f:
        json.dump(all_drafts, f, indent=2)

    print(f"\nSaved {len(drafts)} new draft(s) to {output_path}")
    print(f"Total drafts in file: {len(all_drafts)}")


def main():
    print("=" * 80)
    print("SourceBox Article Drafter")
    print("=" * 80)

    # Fetch existing articles from website
    print("\nStep 1: Fetching existing articles from website...")
    articles = fetch_all_articles()
    print(f"\nFetched {len(articles)} articles from website.")

    if not articles:
        print("No articles found. Exiting.")
        return

    # Analyze existing articles
    print("\nStep 2: Analyzing existing articles...")
    themes = analyze_existing_articles(articles)

    # Generate new article ideas
    print("\nStep 3: Generating new article ideas...")
    num_ideas = int(os.getenv("NUM_IDEAS", "3"))
    ideas = generate_article_ideas(themes, num_ideas=num_ideas)

    if not ideas:
        print("Could not generate article ideas. Exiting.")
        return

    print(f"\nGenerated {len(ideas)} article ideas:")
    for i, idea in enumerate(ideas, 1):
        print(f"\n{i}. {idea['title']}")
        print(f"   {idea['description']}")

    # Generate full drafts for each idea
    print("\nStep 4: Generating full article drafts...")
    drafts = []
    for idea in ideas:
        draft_content = generate_article_draft(idea)
        draft = {
            "title": idea["title"],
            "description": idea["description"],
            "content": draft_content,
        }
        drafts.append(draft)
        create_notion_page_for_draft(draft)
        print(f"Generated draft for: {idea['title']}")

    # Save drafts
    print("\nStep 5: Saving drafts...")
    save_drafts(drafts)

    print("\n" + "=" * 80)
    print("Article drafting complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()