"""
Utilities for fetching and converting PR HTML pages.
"""

import re
import subprocess
from typing import Optional


def _fetch_pr_html(pr_url: str) -> Optional[str]:
    """Fetch PR HTML page using curl.

    Args:
        pr_url: The PR URL to fetch

    Returns:
        HTML content as string, or None if fetch fails
    """
    try:
        result = subprocess.run(
            ["curl", "-L", "-s", pr_url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        # Silently fail on network/timeout errors - HTML fetch is optional
        pass
    return None


def _html_to_simple_markdown(html: Optional[str]) -> str:
    """Convert HTML to simple markdown for better readability.

    This is a basic conversion without external dependencies.
    It extracts text content and attempts to preserve structure.

    Improvements:
    - Removes header content before prc-PageLayout-Content div
    - Removes footer content and everything after
    - Consolidates consecutive blank lines (including space-only lines)
    - Preserves whitespace inside code blocks (pre/code tags)

    Args:
        html: HTML content as string, or None

    Returns:
        Simplified markdown representation
    """
    if not html:
        return ""

    text = html

    # Remove header content: keep only content from prc-PageLayout-Content onwards
    # Look for the div with class containing "prc-PageLayout-Content"
    content_match = re.search(r'<div[^>]*class="[^"]*prc-PageLayout-Content[^"]*"[^>]*>', text, flags=re.IGNORECASE)
    if content_match:
        # Keep everything from this div onwards
        text = text[content_match.start() :]

    # Remove footer content: remove everything from <footer> tag onwards
    footer_match = re.search(r"<footer[^>]*>", text, flags=re.IGNORECASE)
    if footer_match:
        # Keep everything before the footer
        text = text[: footer_match.start()]

    # Remove script and style tags with their content
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Convert common HTML elements to markdown
    # Headers
    text = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n# \1\n", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", text, flags=re.DOTALL | re.IGNORECASE)

    # Links
    text = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r"[\2](\1)", text, flags=re.DOTALL | re.IGNORECASE)

    # Bold and italic
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", text, flags=re.DOTALL | re.IGNORECASE)

    # Code blocks
    text = re.sub(r"<pre[^>]*>(.*?)</pre>", r"```\n\1\n```", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.DOTALL | re.IGNORECASE)

    # Lists
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", text, flags=re.DOTALL | re.IGNORECASE)

    # Paragraphs and line breaks
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n\n", text, flags=re.DOTALL | re.IGNORECASE)

    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean up HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    # Clean up excessive whitespace while preserving code block formatting
    # Process line by line to consolidate blank lines without affecting code blocks
    lines = text.split("\n")
    cleaned_lines = []
    prev_blank = False
    in_code_block = False

    for line in lines:
        # Track code block boundaries (markdown fenced code blocks)
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            cleaned_lines.append(line)
            prev_blank = False
            continue

        # Inside code blocks, preserve all whitespace exactly as-is
        if in_code_block:
            cleaned_lines.append(line)
            prev_blank = False
            continue

        # Outside code blocks, consolidate blank lines and normalize leading/trailing spaces
        is_blank = line.strip() == ""
        if is_blank:
            if not prev_blank:
                cleaned_lines.append("")
            prev_blank = True
        else:
            # For non-blank lines outside code blocks, only strip trailing whitespace
            # Keep leading whitespace for list indentation, but normalize multiple spaces
            cleaned_lines.append(line.rstrip())
            prev_blank = False

    text = "\n".join(cleaned_lines)

    return text.strip()
