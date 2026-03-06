with open("core/tools/context_scraper.py", "r") as f:
    content = f.read()

content = content.replace(
    "scraper = AetherContextScraper)", "scraper = AetherContextScraper()"
)

with open("core/tools/context_scraper.py", "w") as f:
    f.write(content)
