import re
from email import message_from_bytes
from email.header import decode_header

from html2text import html2text


class Email:
    def __init__(self, email):
        self._email = email
        self._structure = None

    @property
    def structure(self):
        return self._structure

    def parse(self):
        message = message_from_bytes(self._email)
        headers = dict(message.items())
        body = markdown = simple_markdown = ""
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
            markdown = html2text(body, bodywidth=0)
            simple_markdown = markdown.replace("\r", "")
            simple_markdown = re.sub("\n\n+", "\n", simple_markdown)
            simple_markdown = simple_markdown[:500].strip()

        structure = {
            'headers': headers,
            'subject': self._get_subject(headers["Subject"]),
            'body': body,
            'markdown': markdown,
            'simple_markdown': simple_markdown,
        }

        self._structure = structure

        return structure

    @staticmethod
    def _get_subject(header):
        subject = ""
        for part in decode_header(header):
            if type(part[0]) is str:
                subject += part[0]
            else:
                subject += part[0].decode(part[1] if part[1] is not None else "utf-8")

        return subject.replace("\r\n", "")
