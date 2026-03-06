with open("core/tools/context_scraper.py", "r") as f:
    content = f.read()

content = content.replace("<<<<<<< HEAD", "")
content = content.replace("=======", "")
content = content.replace(">>>>>>> origin/jules-3466090822907057400-4af64808", "")
content = content.replace(
    "self.fetcher = Fetcherauto_match=True)", "self.fetcher = Fetcher(auto_match=True)"
)

with open("core/tools/context_scraper.py", "w") as f:
    f.write(content)
