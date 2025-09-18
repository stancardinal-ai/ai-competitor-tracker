#!/usr/bin/env python3
"""
Simple Anthropic News Scraper
This script fetches the latest news and updates from Anthropic's website
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json


def fetch_anthropic_news():
    """
    Fetch and parse Anthropic's news page
    Returns a list of news post information
    """

    # Anthropic's news URL
    url = "https://www.anthropic.com/news"

    # Headers to appear like a regular browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    print("🔍 Fetching Anthropic's news page...")

    try:
        # Make the HTTP request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes

        print("✅ Successfully fetched the page!")

    except requests.RequestException as e:
        print(f"❌ Error fetching the page: {e}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    print(f"  Debug: Page size: {len(response.text)} characters")

    # Find news posts
    news_posts = []

    # Find the main content area first
    main_content = soup.find('main')
    if not main_content:
        print("  Debug: No main tag found, using entire page")
        main_content = soup  # Fall back to entire page
    else:
        print(f"  Debug: Found main tag with {len(str(main_content))} characters")

    # Look for news links - Anthropic has links with /news/ or /research/ in the URL
    news_links = main_content.find_all('a', href=lambda x: x and ('/news/' in x or '/research/' in x))

    print(f"  Debug: Found {len(news_links)} total news/research links")

    # Filter out duplicates based on href, not full link object
    seen_urls = set()
    unique_links = []
    for link in news_links:
        href = link.get('href', '')
        # Keep internal links (starting with /)
        if href and href not in seen_urls and (href.startswith('/news/') or href.startswith('/research/')):
            seen_urls.add(href)
            unique_links.append(link)

    print(f"📰 Found {len(unique_links)} unique news posts")

    for i, link in enumerate(unique_links[:15], 1):  # Limit to 15 posts
        post_data = {}

        # Get the link URL
        href = link.get('href', '')
        if href:
            # Make sure it's a full URL
            if href.startswith('/'):
                href = f"https://www.anthropic.com{href}"
            post_data['link'] = href

        # Get the title from the link text
        link_text = link.get_text(strip=True)

        # Sometimes the text includes category + title, let's clean it
        # Remove common prefixes like "Announcements", "Policy", "Research", etc.
        categories = ['Announcements', 'Policy', 'Research', 'Product', 'Societal Impacts']
        for category in categories:
            if link_text.startswith(category):
                post_data['category'] = category
                link_text = link_text[len(category):].strip()
                break

        if link_text:
            post_data['title'] = link_text

        # Add to list if we have at least a title and link
        if 'title' in post_data and 'link' in post_data:
            news_posts.append(post_data)
            print(f"  {i}. {post_data.get('category', 'News')}: {post_data['title'][:50]}...")

    return news_posts


def save_results(news_posts):
    """
    Save the scraped news posts to a JSON file and markdown report
    """

    # Save as JSON for easy processing
    json_filename = f"anthropic_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(news_posts, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved raw data to: {json_filename}")

    # Create a markdown report
    report_filename = f"reports/anthropic_report_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("# Anthropic News Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Source:** https://www.anthropic.com/news\n\n")
        f.write("---\n\n")

        if news_posts:
            f.write(f"## Latest {len(news_posts)} News Posts\n\n")
            for i, post in enumerate(news_posts, 1):
                f.write(f"### {i}. {post.get('title', 'Untitled')}\n\n")
                if 'category' in post:
                    f.write(f"**Category:** {post['category']}\n\n")
                if 'link' in post:
                    f.write(f"**Link:** {post['link']}\n\n")
                if 'date' in post:
                    f.write(f"**Date:** {post['date']}\n\n")
                if 'description' in post:
                    f.write(f"**Summary:** {post['description']}\n\n")
                f.write("---\n\n")
        else:
            f.write("No news posts found. The website structure might have changed.\n")

    print(f"📄 Saved report to: {report_filename}")

    return report_filename


def main():
    """
    Main function to run the scraper
    """
    print("=" * 50)
    print("🤖 Anthropic News Scraper")
    print("=" * 50)
    print("\nThis scraper fetches the latest news from Anthropic,")
    print("the company that created Claude!\n")

    # Fetch news posts
    news_posts = fetch_anthropic_news()

    if news_posts:
        print(f"\n✨ Successfully scraped {len(news_posts)} news posts!")

        # Save the results
        report_file = save_results(news_posts)

        print("\n" + "=" * 50)
        print("✅ Scraping complete!")
        print("=" * 50)

        # Display first few posts as preview
        print("\n📋 Preview of scraped posts:")
        for i, post in enumerate(news_posts[:3], 1):
            print(f"\n{i}. {post.get('title', 'Untitled')}")
            if 'link' in post:
                print(f"   Link: {post['link']}")
            if 'description' in post:
                print(f"   Summary: {post.get('description', '')[:100]}...")
    else:
        print("\n⚠️  No news posts were found.")
        print("This could mean:")
        print("1. The website structure has changed")
        print("2. The site is blocking our request")
        print("3. Network connection issues")
        print("\nTry checking your internet connection and running again.")


if __name__ == "__main__":
    main()