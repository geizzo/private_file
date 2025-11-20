#!/usr/bin/env python3
"""Download lesson quiz questions from a Multiversity LMS lesson page.

The script fetches the provided URL, locates the section titled
"Test di fine lezione", and extracts the questions that appear under that
heading until the next heading of equal or higher rank. Extracted questions
are printed to stdout and can optionally be written to a file.
"""

import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Iterable, List


DEFAULT_USERNAME = "drosa_0162500434"
DEFAULT_PASSWORD = "0cdbb4e6"
DEFAULT_URL = "https://lms.utsr.multiversity.click/videolezioni/0162206INF01/4"


_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_BLOCK_TAGS = {"li", "p", "div"}


def _heading_level(tag: str) -> int:
    """Return an integer level for the given heading tag (h1 -> 1)."""
    if tag.startswith("h") and tag[1:].isdigit():
        return int(tag[1:])
    return 7


class LessonTestParser(HTMLParser):
    """HTML parser that collects questions under the target heading."""

    def __init__(self) -> None:
        super().__init__()
        self.in_heading = False
        self.heading_buffer: List[str] = []
        self.pending_heading_level: int | None = None
        self.collecting = False
        self.section_heading_level: int | None = None
        self.current_block_tag: str | None = None
        self.current_block_buffer: List[str] = []
        self.questions: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        if tag in _HEADING_TAGS:
            self.in_heading = True
            self.heading_buffer.clear()
            self.pending_heading_level = _heading_level(tag)

        if self.collecting and tag in _BLOCK_TAGS:
            self.current_block_tag = tag
            self.current_block_buffer.clear()

    def handle_data(self, data: str) -> None:
        if self.in_heading:
            self.heading_buffer.append(data)
        if self.collecting and self.current_block_tag:
            self.current_block_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.in_heading and tag in _HEADING_TAGS:
            heading_raw = " ".join("".join(self.heading_buffer).split())
            heading_text = heading_raw.lower()
            level = self.pending_heading_level

            if "test di fine lezione" in heading_text:
                self.collecting = True
                self.section_heading_level = level
            elif self.collecting and self.section_heading_level is not None and level is not None:
                if level <= self.section_heading_level:
                    first_token = heading_text.split()[0] if heading_text else ""
                    is_numbered_heading = first_token.rstrip(".").isdigit()
                    if not is_numbered_heading:
                        self.collecting = False
                        self.current_block_tag = None
                        self.current_block_buffer.clear()

                if self.collecting:
                    first_token = heading_text.split()[0] if heading_text else ""
                    is_numbered_heading = first_token.rstrip(".").isdigit()
                    if is_numbered_heading or (level > self.section_heading_level and heading_text):
                        self.questions.append(heading_raw)
            self.in_heading = False
            self.heading_buffer.clear()
            self.pending_heading_level = None

        if self.collecting and tag == self.current_block_tag:
            text = " ".join("".join(self.current_block_buffer).split())
            if text:
                self.questions.append(text)
            self.current_block_tag = None
            self.current_block_buffer.clear()


def fetch_html(url: str, username: str | None = None, password: str | None = None) -> str:
    """Fetch and decode HTML from the given URL, optionally with basic auth."""

    password_mgr = None
    opener = None

    if username and password:
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, username, password)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)

    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    if opener:
        with opener.open(request) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")

    with urllib.request.urlopen(request) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def extract_questions(html: str) -> List[str]:
    """Parse the HTML and return unique questions from the target section."""
    parser = LessonTestParser()
    parser.feed(html)
    parser.close()

    seen = set()
    questions: List[str] = []
    for question in parser.questions:
        if question not in seen:
            questions.append(question)
            seen.add(question)
    return questions


def save_questions(questions: Iterable[str], path: str) -> None:
    """Write questions to a file, one per line."""
    with open(path, "w", encoding="utf-8") as file:
        for question in questions:
            file.write(f"{question}\n")


def main(argv: List[str]) -> int:
    url = argv[0] if argv else DEFAULT_URL
    output_path = argv[1] if len(argv) > 1 else None
    try:
        html = fetch_html(url, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)
    except urllib.error.URLError as exc:
        print(f"Errore di rete durante il download: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Errore di connessione durante il download: {exc}", file=sys.stderr)
        return 2

    questions = extract_questions(html)

    if not questions:
        print("Nessuna domanda trovata nella sezione 'Test di fine lezione'.", file=sys.stderr)
        return 1

    if output_path:
        save_questions(questions, output_path)

    for index, question in enumerate(questions, start=1):
        print(f"{index}. {question}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
