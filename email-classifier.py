import argparse
import math
import os
import re
from datetime import timedelta
from email import message_from_bytes
from email.header import decode_header

from html2text import html2text
from ollama import ChatResponse
from ollama import chat


def get_subject(header):
    subject = ""
    for part in decode_header(header):
        if type(part[0]) is str:
            subject += part[0]
        else:
            subject += part[0].decode(part[1] if part[1] is not None else "utf-8")

    return subject.replace("\r\n", "")


def extract_mail_content(directory):
    email_content = []
    for filename in os.listdir(directory):
        if filename.endswith(".eml"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'rb') as file:
                message = message_from_bytes(file.read())
                headers = dict(message.items())
                if message.is_multipart():
                    for part in message.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get('Content-Disposition'))

                        if content_type != "text/html" or "attachment" in content_disposition:
                            continue

                        try:
                            body = part.get_payload(decode=True).decode()
                            break
                        except:
                            pass
                else:
                    body = message.get_payload(decode=True).decode()

                markdown = html2text(body, bodywidth=0)
                simple_markdown = markdown.replace("\r", "")
                simple_markdown = re.sub("\n\n+", "\n", simple_markdown)
                simple_markdown = simple_markdown[:500]

                email_dict = {
                    'headers': headers,
                    'subject': get_subject(headers["Subject"]),
                    'body': body,
                    'markdown': markdown,
                    'simple_markdown': simple_markdown,
                }
                email_content.append(email_dict)
    return email_content


def process_mails(directory):
    mails = extract_mail_content(directory)

    for mail in mails:
        print(f'"{get_subject(mail["subject"])}": ', end="", flush=True)

        response: ChatResponse = chat(model='mistral:7b', messages=[
            {
                'role': 'user',
                'content': f"Classify the following e-mail given in markdown format into one of the following four categories: "
                           "'primary', 'promotion', 'social', 'notification'. If unsure, output the string 'unsure' verbatim. "
                           "The response must contain only one word: one of the listed categories or 'unsure'.\n"
                           f"Email content:\n{mail["subject"]}\n{mail["simple_markdown"]}",
            },
        ])

        classification = response["message"]["content"].strip().replace("'", "")
        print(
            f"{classification} "
            f"(prompt: {timedelta(seconds=math.ceil(response["prompt_eval_duration"] / (10 ** 9)))}, "
            f"total: {timedelta(seconds=math.ceil(response["total_duration"] / (10 ** 9)))} sec)"
        )


def main():
    parser = argparse.ArgumentParser(description='E-mail classifier comparator')
    parser.add_argument('directory', help='Path to the directory containing the .eml files', type=str)
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"The directory '{args.directory}' does not exist.")
        exit(1)

    process_mails(args.directory)


if __name__ == "__main__":
    main()
