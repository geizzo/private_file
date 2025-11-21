#!/usr/bin/env python3
"""Download lesson quiz questions from a Multiversity LMS lesson page.

The script fetches the provided URL, locates the section titled
"Test di fine lezione", and extracts the questions that appear under that
heading until the next heading of equal or higher rank. Extracted questions
are printed to stdout and can optionally be written to a file.
"""

import shutil
import sys
from html.parser import HTMLParser
from typing import Iterable, List

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService


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


def _inject_basic_auth(url: str, username: str | None, password: str | None) -> str:
    """Return the URL with embedded basic-auth credentials if provided."""

    if not username or not password:
        return url

    if "//" not in url:
        return url

    scheme, rest = url.split("//", 1)
    return f"{scheme}//{username}:{password}@{rest}"


def _build_driver() -> webdriver.Remote:
    """Initialize a headless Selenium driver using an available browser."""

    chrome_driver = shutil.which("chromedriver")
    if chrome_driver:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(service=ChromeService(executable_path=chrome_driver), options=options)

    firefox_driver = shutil.which("geckodriver")
    if firefox_driver:
        options = FirefoxOptions()
        options.add_argument("-headless")
        return webdriver.Firefox(service=FirefoxService(executable_path=firefox_driver), options=options)

    raise RuntimeError(
        "Nessun driver Selenium disponibile. Installa chromedriver o geckodriver e assicurati che siano nel PATH."
    )


def fetch_html(url: str, username: str | None = None, password: str | None = None, timeout: int = 60) -> str:
    """Fetch HTML from the given URL using Selenium with optional basic auth."""

    driver = _build_driver()
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(_inject_basic_auth(url, username, password))
        return driver.page_source
    finally:
        driver.quit()


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
    except (WebDriverException, TimeoutException, RuntimeError) as exc:
        print(f"Errore durante il download con Selenium: {exc}", file=sys.stderr)
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
