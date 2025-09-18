#!/usr/bin/env python3
"""
Debug script to understand Anthropic's website structure
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.anthropic.com/news"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Fetching page...")
response = requests.get(url, headers=headers)
print(f"Status code: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Save the HTML to inspect it
    with open('anthropic_page.html', 'w') as f:
        f.write(response.text[:5000])  # First 5000 chars

    print("\nLooking for different element types:")

    # Check for different possible containers
    print(f"Articles: {len(soup.find_all('article'))}")
    print(f"Divs with 'news': {len(soup.find_all('div', class_=lambda x: x and 'news' in str(x).lower()))}")
    print(f"Divs with 'post': {len(soup.find_all('div', class_=lambda x: x and 'post' in str(x).lower()))}")
    print(f"Links with /news/: {len(soup.find_all('a', href=lambda x: x and '/news/' in x))}")

    # Look for any h2, h3 tags which might be titles
    headings = soup.find_all(['h2', 'h3'])[:5]
    print(f"\nFirst 5 headings found:")
    for h in headings:
        print(f"  - {h.get_text(strip=True)[:60]}")

    # Check main content areas
    main = soup.find('main')
    if main:
        print(f"\nFound <main> tag with {len(str(main))} characters")
        # Look for links within main
        links = main.find_all('a', href=lambda x: x and ('/news/' in x or '/research/' in x))
        print(f"Found {len(links)} news/research links in main")

        # Check for duplicates
        seen = set()
        unique = []
        for link in links:
            href = link.get('href', '')
            if href not in seen:
                seen.add(href)
                unique.append(link)

        print(f"After filtering duplicates: {len(unique)} unique links")
        print(f"\nFirst 10 unique links:")
        for link in unique[:10]:
            print(f"  - {link.get('href')}: {link.get_text(strip=True)[:40]}")