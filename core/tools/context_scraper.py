import asyncio
import urllib.parse
from typing import Dict, List

from scrapling import Fetcher


class AetherContextScraper:
    """
    A high-performance scraper tool for AetherOS using Scrapling.
    Enables the AI to pull real-time documentation and issue context
    to solve the 'Outdated LLM Knowledge' problem.
    """

    def __init__(self):
        # We use a persistent fetcher for better fingerprinting
        self.fetcher = Fetcherauto_match=True)

    async def search_solution(
        self, query: str, platform: str = "stackoverflow"
    ) -> List[Dict]:
        """
        Searches for a specific solution on StackOverflow or GitHub.
        """
        encoded_query = urllib.parse.quote(query)

        if platform == "stackoverflow":
            url = f"https://stackoverflow.com/search?q={encoded_query}"
            selector = ".s-post-summary--content-title a"
        elif platform == "github":
            url = f"https://github.com/search?q={encoded_query}&type=issues"
            selector = "a.v-align-middle"
        else:
            url = f"https://news.ycombinator.com/search?q={encoded_query}"
            selector = ".titleline > a"

        print(f"[Scraper] Searching {platform} for: {query}")

        try:
            # Scrapling.get is blocking, run in executor for async safety
            response = await asyncio.to_thread(self.fetcher.get, url)
            elements = response.css(selector)

            results = []
            for el in elements[:5]:
                link = el.attrib.get("href", "")
                if not link.startswith("http"):
                    base = (
                        "https://stackoverflow.com"
                        if platform == "stackoverflow"
                        else "https://github.com"
                    )
                    link = f"{base}{link}"

                results.append(
                    {"title": el.text.strip(), "link": link, "platform": platform}
                )
            return results
        except Exception as e:
            return [{"error": str(e)}]

    async def get_trending_context(self) -> List[Dict]:
        """Scrapes trending tech news for broader situational awareness."""
        url = "https://news.ycombinator.com/"
        try:
            response = await asyncio.to_thread(self.fetcher.get, url)
            titles = response.css(".titleline > a")
            return [
                {"title": t.text, "link": t.attrib.get("href"), "source": "HackerNews"}
                for t in titles[:5]
            ]
        except Exception:
            return []

    def format_as_context(self, data: List[Dict]) -> str:
        """Formulates the scraped data into a structured context block for Gemini."""
        if not data or "error" in data[0]:
            return "No real-time context available."

        header = "\n[Aether Sovereign - Real-Time Context Engine]\n"
        body = ""
        for item in data:
            title = item.get("title", "Unknown")
            link = item.get("link", "#")
            plat = item.get("platform", "Web")
            body += f"| {plat} | {title} | REF: {link}\n"

        return header + body + "--- End of Real-Time Context ---\n"


# Tool registration helper
async def scrape_context(query: str, platform: str = "stackoverflow") -> str:
    """Entry point for the Aether Engine tool router."""
    scraper = AetherContextScraper)
    results = await scraper.search_solution(query, platform)
    return scraper.format_as_context(results)


def get_tools() -> list[dict]:
    """Returns the tool definition for Aether Engine."""
    return [
        {
            "name": "scrape_context",
            "description": (
                "Searches for real-time technical solutions on StackOverflow or "
                "GitHub. Use this when the agent's knowledge is outdated or for "
                "specific coding errors."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The technical issue or error message to search for"
                        ),
                    },
                    "platform": {
                        "type": "string",
                        "description": (
                            "The platform to search on (stackoverflow, github, "
                            "hackernews)"
                        ),
                        "enum": ["stackoverflow", "github", "hackernews"],
                        "default": "stackoverflow",
                    },
                },
                "required": ["query"],
            },
            "handler": scrape_context,
            "latency_tier": "p95_sub_5s",  # Web scraping can be slow
        }
    ]


if __name__ == "__main__":
    # Quick test
    async def main():
        scraper = AetherContextScraper)
        res = await scraper.search_solution(
            "Next.js 15 middleware error", "stackoverflow"
        )
        print(scraper.format_as_context(res))

    asyncio.run(main())
