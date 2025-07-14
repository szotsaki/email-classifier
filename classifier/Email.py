import re
import unicodedata
from email import message_from_bytes
from email.header import decode_header
from typing import TypedDict

import html2text
from bs4 import BeautifulSoup


class EmailStructure(TypedDict):
    headers: dict | None
    subject: str | None
    body: str | None
    markdown: str | None


class Email:
    def __init__(self, email: bytes):
        self._email = email
        self._structure = None

        h2t = html2text.HTML2Text()
        h2t.body_width = 0
        h2t.ignore_images = True
        h2t.ignore_links = True
        h2t.inline_links = False
        h2t.ignore_tables = True

        self._html2text = h2t.handle

    @property
    def structure(self) -> EmailStructure | None:
        return self._structure

    def parse(self, markdown_limit=300) -> EmailStructure:
        message = message_from_bytes(self._email)
        headers = dict(message.items())
        subject = self._get_subject(headers["Subject"]) if "Subject" in headers else ""
        body = markdown = ""
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))

                if content_type not in ["text/plain", "text/html"] or "attachment" in content_disposition:
                    continue

                charset = part.get_param('charset', 'ASCII')
                body = part.get_payload(decode=True).decode(charset)
        else:
            charset = message.get_param('charset', 'ASCII')
            body = message.get_payload(decode=True).decode(charset)

        if body:
            # Fix broken HTML and remove superfluous Unicode characters
            html = str(BeautifulSoup(body, 'html5lib'))
            # Remove Unicode control and mark characters - https://www.unicode.org/reports/tr44/#General_Category_Values
            html = ''.join(c for c in html if not (unicodedata.category(c)[0] in ['C', 'M']) or c == "\n")
            html = re.sub(r"\s+", " ", html)  # \s catches Unicode whitespaces

            markdown = self._html2text(html)
            markdown = re.sub(r"(\s*\n)+", r"\n", markdown)
            markdown = markdown[:markdown_limit].strip()

        structure: EmailStructure = {
            'headers': headers,
            'subject': subject,
            'body': body,
            'markdown': markdown,
        }

        self._structure = structure

        return structure

    @staticmethod
    def _get_subject(header: str) -> str:
        subject = ""
        for part in decode_header(header):
            if type(part[0]) is str:
                subject += part[0]
            else:
                subject += part[0].decode(part[1] if part[1] is not None else "utf-8")

        return subject.replace("\r\n", "")
