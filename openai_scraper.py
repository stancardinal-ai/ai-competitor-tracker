#!/usr/bin/env python3
"""
Simple OpenAI Blog Scraper
This script fetches the latest blog posts from OpenAI's website
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json


def fetch_openai_blog():
    """
    Fetch and parse OpenAI's blog page
    Returns a list of blog post information
    """

    # OpenAI's blog URL
    url = "https://openai.com/news/"

    # Headers to appear like a regular browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("🔍 Fetching OpenAI's blog page...")

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

    # Find blog posts - OpenAI uses different structures, so we'll try multiple approaches
    blog_posts = []

    # Look for article elements or divs that contain blog posts
    # Note: Website structures change, so we'll use flexible selectors
    articles = soup.find_all(['article', 'div'], class_=lambda x: x and any(
        keyword in x.lower() for keyword in ['post', 'article', 'story', 'card']
    )) if soup else []

    # Also try finding by common blog post patterns
    if not articles:
        articles = soup.select('a[href*="/blog/"], a[href*="/news/"]')[:10]

    print(f"📰 Found {len(articles)} potential blog posts")

    for i, article in enumerate(articles[:10], 1):  # Limit to 10 posts
        post_data = {}

        # Try to extract title
        title_elem = None
        if hasattr(article, 'find'):
            # Look for headings
            title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        if title_elem:
            post_data['title'] = title_elem.get_text(strip=True)
        else:
            # Try to get text from the article itself
            post_data['title'] = article.get_text(strip=True)[:100] + "..."

        # Try to extract link
        link_elem = article.find('a') if hasattr(article, 'find') else article
        if link_elem and link_elem.has_attr('href'):
            href = link_elem['href']
            # Make sure it's a full URL
            if href.startswith('/'):
                href = f"https://openai.com{href}"
            post_data['link'] = href

        # Try to extract date or description
        date_elem = article.find(['time', 'span'], class_=lambda x: x and 'date' in x.lower()) if hasattr(article, 'find') else None
        if date_elem:
            post_data['date'] = date_elem.get_text(strip=True)

        # Add to list if we have at least a title
        if 'title' in post_data and post_data['title']:
            blog_posts.append(post_data)
            print(f"  {i}. {post_data['title'][:60]}...")

    return blog_posts


def save_results(blog_posts):
    """
    Save the scraped blog posts to a JSON file and markdown report
    """

    # Save as JSON for easy processing
    json_filename = f"openai_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(blog_posts, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved raw data to: {json_filename}")

    # Create a markdown report
    report_filename = f"reports/openai_report_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("# OpenAI Blog Posts Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Source:** https://openai.com/news/\n\n")
        f.write("---\n\n")

        if blog_posts:
            f.write(f"## Latest {len(blog_posts)} Blog Posts\n\n")
            for i, post in enumerate(blog_posts, 1):
                f.write(f"### {i}. {post.get('title', 'Untitled')}\n")
                if 'link' in post:
                    f.write(f"**Link:** {post['link']}\n")
                if 'date' in post:
                    f.write(f"**Date:** {post['date']}\n")
                f.write("\n")
        else:
            f.write("No blog posts found. The website structure might have changed.\n")

    print(f"📄 Saved report to: {report_filename}")

    return report_filename


def main():
    """
    Main function to run the scraper
    """
    print("=" * 50)
    print("🤖 OpenAI Blog Scraper")
    print("=" * 50)

    # Fetch blog posts
    blog_posts = fetch_openai_blog()

    if blog_posts:
        print(f"\n✨ Successfully scraped {len(blog_posts)} blog posts!")

        # Save the results
        report_file = save_results(blog_posts)

        print("\n" + "=" * 50)
        print("✅ Scraping complete!")
        print("=" * 50)

        # Display first few posts as preview
        print("\n📋 Preview of scraped posts:")
        for i, post in enumerate(blog_posts[:3], 1):
            print(f"\n{i}. {post.get('title', 'Untitled')}")
            if 'link' in post:
                print(f"   Link: {post['link']}")
    else:
        print("\n⚠️  No blog posts were found. The website might be unavailable or the structure has changed.")
        print("You might need to update the selectors in the script.")


if __name__ == "__main__":
    main()