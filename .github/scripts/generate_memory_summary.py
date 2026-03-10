import os
import sys

from google import genai


def generate_summary():
    diff_file = sys.argv[1]

    with open(diff_file, 'r', encoding='utf-8') as f:
        diff_content = f.read()

    # Truncate diff if it's too large for the context window (basic protection)
    # Gemini 1.5 Flash supports very large context, but let's keep it reasonable
    if len(diff_content) > 500000:
        diff_content = diff_content[:500000] + "\n... [DIFF TRUNCATED]"

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an expert software engineer and technical writer. Please analyze the following Git diff and provide a smart, well-written, and real analysis/summary of the changes.

Make the summary concise but informative. Focus on *what* changed and *why* it matters, not just a line-by-line regurgitation of the diff.
Do not use a generic "this commit updates X" template. Be insightful.

Format your response in Markdown.

Here is the Git diff:
```diff
{diff_content}
```
"""

    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        print(response.text)
    except Exception as e:
        print(f"Failed to generate summary via Gemini API: {e}")
        # Fallback to basic summary if API fails
        print("Summary generation failed. Check action logs for details.")

if __name__ == "__main__":
    generate_summary()
