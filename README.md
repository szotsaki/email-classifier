# Local e-mail classifier with AI

This is a simple script that uses Ollama to locally classify emails in the provided directory.

Usage:

1. Install [Ollama](https://ollama.com/download) and its [Python binding](https://github.com/ollama/ollama-python), then start the service
2. Download the Mistral model: `ollama pull mistral:7b`
3. Export some of your e-mails into a directory (e.g. from Thunderbird) in .eml format (where both the headers and body are present)
4. Run this program with this directory as an argument