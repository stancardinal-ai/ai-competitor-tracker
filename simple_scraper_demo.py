#!/usr/bin/env python3
"""
Simple Web Scraper Demo
This demonstrates how web scraping works with a working example
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json


def scrape_hacker_news():
    """
    Scrape Hacker News - a simple, scrape-friendly site
    Returns the top stories
    """

    url = "https://news.ycombinator.com"

    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Educational Bot)'
    }

    print("🔍 Fetching Hacker News top stories...")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print("✅ Successfully fetched the page!")
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return []

    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find story titles - they're in <span class="titleline">
    stories = []
    story_rows = soup.find_all('tr', class_='athing')[:10]  # Get top 10 stories

    for story in story_rows:
        story_data = {}

        # Get the title and link
        titleline = story.find('span', class_='titleline')
        if titleline:
            link_tag = titleline.find('a')
            if link_tag:
                story_data['title'] = link_tag.get_text(strip=True)
                story_data['link'] = link_tag.get('href', '')

                # Make relative links absolute
                if story_data['link'].startswith('item?'):
                    story_data['link'] = f"https://news.ycombinator.com/{story_data['link']}"

        # Get the score (in the next row)
        next_row = story.find_next_sibling('tr')
        if next_row:
            score = next_row.find('span', class_='score')
            if score:
                story_data['score'] = score.get_text(strip=True)

            # Get comment count
            comments = next_row.find('a', string=lambda x: x and 'comment' in x)
            if comments:
                story_data['comments'] = comments.get_text(strip=True)

        if 'title' in story_data:
            stories.append(story_data)

    return stories


def scrape_with_sample_data():
    """
    Returns sample data to demonstrate how the scraper would work
    with AI company news sites that use JavaScript
    """

    print("🤖 Since many AI company sites use JavaScript,")
    print("here's what the scraped data would look like:\n")

    sample_data = [
        {
            'title': 'Claude Opus 4.1 - Our Most Powerful Model Yet',
            'link': 'https://www.anthropic.com/news/claude-opus-4-1',
            'category': 'Announcement',
            'date': '2025-01-15'
        },
        {
            'title': 'Thoughts on America\'s AI Action Plan',
            'link': 'https://www.anthropic.com/news/thoughts-on-americas-ai-action-plan',
            'category': 'Policy',
            'date': '2025-01-14'
        },
        {
            'title': 'Anthropic Raises $13B Series F',
            'link': 'https://www.anthropic.com/news/series-f-funding',
            'category': 'Company News',
            'date': '2025-01-10'
        },
        {
            'title': 'GPT-5 Coming Soon',
            'link': 'https://openai.com/blog/gpt-5-preview',
            'category': 'Product',
            'date': '2025-01-16'
        },
        {
            'title': 'Google Announces Gemini 2.0',
            'link': 'https://blog.google/technology/ai/gemini-2',
            'category': 'Product Launch',
            'date': '2025-01-12'
        }
    ]

    return sample_data


def save_report(stories, source_name):
    """
    Save scraped data as a markdown report
    """

    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    report_file = f"reports/{source_name}_report_{timestamp}.md"

    with open(report_file, 'w') as f:
        f.write(f"# {source_name} Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        for i, story in enumerate(stories, 1):
            f.write(f"## {i}. {story.get('title', 'Untitled')}\n\n")

            if 'link' in story:
                f.write(f"**Link:** {story['link']}\n\n")

            if 'category' in story:
                f.write(f"**Category:** {story['category']}\n\n")

            if 'date' in story:
                f.write(f"**Date:** {story['date']}\n\n")

            if 'score' in story:
                f.write(f"**Score:** {story['score']}\n\n")

            if 'comments' in story:
                f.write(f"**Discussion:** {story['comments']}\n\n")

            f.write("---\n\n")

    print(f"📄 Report saved to: {report_file}")

    # Also save as JSON
    json_file = f"{source_name}_data_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(stories, f, indent=2)

    print(f"💾 Data saved to: {json_file}")


def main():
    """
    Main function
    """
    print("=" * 60)
    print("🌐 WEB SCRAPING DEMONSTRATION")
    print("=" * 60)
    print()

    # First, show a working example with Hacker News
    print("1️⃣  REAL EXAMPLE: Scraping Hacker News")
    print("-" * 40)
    hn_stories = scrape_hacker_news()

    if hn_stories:
        print(f"\n✨ Found {len(hn_stories)} stories!\n")
        for i, story in enumerate(hn_stories[:5], 1):
            print(f"{i}. {story.get('title', 'No title')[:60]}...")
            if 'score' in story:
                print(f"   {story['score']} | {story.get('comments', 'No comments')}")
            print()

        save_report(hn_stories, "hackernews")
    else:
        print("Could not fetch Hacker News stories")

    print("\n" + "=" * 60)

    # Then show sample AI company data
    print("\n2️⃣  SAMPLE DATA: What AI company scraping would return")
    print("-" * 40)
    ai_news = scrape_with_sample_data()

    for i, item in enumerate(ai_news, 1):
        print(f"{i}. [{item['category']}] {item['title']}")
        print(f"   Date: {item['date']}")
        print()

    save_report(ai_news, "ai_companies_sample")

    print("\n" + "=" * 60)
    print("✅ Demonstration complete!")
    print("\n📌 Note: Many modern sites (like OpenAI, Anthropic) use JavaScript")
    print("to load content dynamically, which requires more advanced scraping")
    print("tools like Selenium or Playwright for full functionality.")
    print("=" * 60)


if __name__ == "__main__":
    main()