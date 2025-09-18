#!/usr/bin/env python3
"""
AI Competitor Tracker - Main Scraper
Monitors AI company websites for news and updates
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time


class CompetitorScraper:
    def __init__(self, config_file='config.json'):
        """Initialize the scraper with configuration"""
        self.config = self.load_config(config_file)
        self.reports_dir = 'reports'
        self.ensure_reports_directory()

    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Using default configuration.")
            return self.get_default_config()

    def get_default_config(self):
        """Return default configuration if config file is missing"""
        return {
            "competitors": [
                {
                    "name": "OpenAI",
                    "url": "https://openai.com/blog",
                    "selector": "article"
                }
            ],
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def ensure_reports_directory(self):
        """Create reports directory if it doesn't exist"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def fetch_page(self, url):
        """Fetch a webpage and return the HTML content"""
        headers = {'User-Agent': self.config.get('user_agent', '')}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_content(self, html, selector):
        """Parse HTML content using BeautifulSoup"""
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.select(selector)

        parsed_data = []
        for article in articles[:5]:  # Limit to 5 most recent items
            title = article.find(['h1', 'h2', 'h3', 'h4'])
            title_text = title.get_text(strip=True) if title else "No title found"

            # Try to find a link
            link = article.find('a')
            link_url = link.get('href', '') if link else ''

            parsed_data.append({
                'title': title_text,
                'link': link_url,
                'scraped_at': datetime.now().isoformat()
            })

        return parsed_data

    def scrape_competitor(self, competitor):
        """Scrape a single competitor's website"""
        print(f"Scraping {competitor['name']}...")

        html = self.fetch_page(competitor['url'])
        data = self.parse_content(html, competitor.get('selector', 'article'))

        return {
            'name': competitor['name'],
            'url': competitor['url'],
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

    def scrape_all(self):
        """Scrape all competitors defined in config"""
        results = []

        for competitor in self.config.get('competitors', []):
            result = self.scrape_competitor(competitor)
            results.append(result)

            # Be respectful with delays between requests
            time.sleep(2)

        return results

    def generate_report(self, results):
        """Generate a markdown report from scraped data"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        report_file = os.path.join(self.reports_dir, f'report_{date_str}.md')

        with open(report_file, 'w') as f:
            f.write(f"# AI Competitor Intelligence Report\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for company_data in results:
                f.write(f"## {company_data['name']}\n")
                f.write(f"Source: {company_data['url']}\n\n")

                if company_data['data']:
                    f.write("### Recent Updates:\n")
                    for item in company_data['data']:
                        f.write(f"- **{item['title']}**\n")
                        if item['link']:
                            f.write(f"  - Link: {item['link']}\n")
                else:
                    f.write("No recent updates found.\n")

                f.write("\n---\n\n")

        print(f"Report saved to: {report_file}")
        return report_file

    def run(self):
        """Main execution method"""
        print("Starting AI Competitor Tracker...")
        results = self.scrape_all()
        report_file = self.generate_report(results)
        print("Scraping completed!")
        return report_file


def main():
    """Main entry point"""
    scraper = CompetitorScraper()
    scraper.run()


if __name__ == "__main__":
    main()