# E-mail classifier with local AI

This is a program that runs locally (i.e. without internet access) and classifies your incoming e-mails into categories
that you define.

E-mails are classified into one of the following categories:

- pre-defined categories ("primary", "promotion", "social", "notification" by default, but configurable);
- "unsure" if the local large language model (LLM) is unsure about its category;
- "unknown" if the LLM returns a category that doesn't fit into the above categories;
- "error" if an error occurred during processing.

You can select which LLM model to use for the classification [from the available list](https://ollama.com/search).
By default, it uses mistral:7b.

### Requirements

- Linux: [Ollama](https://ollama.com/download), [socat(1)](https://man.archlinux.org/man/socat1.1.en)
- E-mail connector: IMAP server, preferably [Dovecot](https://dovecot.org)
  with [Sieve support](https://doc.dovecot.org/main/core/plugins/sieve.html).
  Plugin [sieve-extprograms](https://doc.dovecot.org/main/core/plugins/sieve_extprograms.html) has to be enabled
- Python: beautifulsoup4, html2text, ollama-python

### Setup

1. Install the requirements.
2. Start the `classify.py` daemon with the socket UID and GID set to those of the IMAP server.
3. Configure the IMAP server to call `classifier.sh` via the `classification.sieve` Sieve script.
    * For Dovecot-specific instructions, see the [Dovecot setup README](dovecot/README.md).

### Architecture

1. The `classify.py` script opens a UNIX socket that listens for incoming e-mails and, after classification, returns
   with one of the categories.
2. Dovecot is configured to call a Sieve filter, `classification.sieve`, on every incoming e-mail.
3. This Sieve filter receives the e-mail from Dovecot and passes it to `classifier.sh`
4. `classifier.sh` receives the e-mail from the Sieve filter and passes it to the previously opened UNIX socket with the
   help of `vnd.dovecot.execute` extension.
5. The result arrives from `classify.py` and the Sieve filter applies the recommended flag.
6. Dovecot, based on the flag, sorts the e-mail into one of the virtual folders under INBOX.

### Usage

```text
usage: classify.py [-h] [-s SOCKET] [--socket-uid SOCKET_UID] [--socket-gid SOCKET_GID] [--max-size MAX_SIZE] [-t TIMEOUT] [-m MODEL]

E-mail classifier

options:
  -h, --help            show this help message and exit
  -s, --socket SOCKET   UNIX socket path to listen on incoming e-mails. Default: /run/email-classifier/classify.sock
  --socket-uid SOCKET_UID
                        UID (user id) of the created UNIX socket
  --socket-gid SOCKET_GID
                        GID (group id) of the created UNIX socket
  --max-size MAX_SIZE   Maximum size (in bytes) of an e-mail to be processed. Default: 30 MiB
  -t, --timeout TIMEOUT
                        Timeout (in seconds) for an e-mail to arrive through the socket. Default: 10 seconds
  -m, --model MODEL     Model to use for classification. Default: mistral:7b
```

## Benchmark

This script uses Ollama to locally classify emails in the provided directory.

Usage:

1. Install [Ollama](https://ollama.com/download) and its [Python binding](https://github.com/ollama/ollama-python), then
   start `ollama.service`.
2. Export some of your e-mails into a directory (e.g. from Thunderbird) in .eml format (where both the headers and the
   body are present).
3. Run `benchmark.py` with this directory as the argument.

```text
usage: benchmark.py [-h] [-m MODELS [MODELS ...]] [--unsure-analysis-dir UNSURE_ANALYSIS_DIR] directory

E-mail classifier comparator

positional arguments:
  directory             Path to the directory containing the .eml files

options:
  -h, --help            show this help message and exit
  -m, --models MODELS [MODELS ...]
                        Models to benchmark. Example: "mistral:7b deepseek-r1:8b". Default: mistral:7b
  --unsure-analysis-dir UNSURE_ANALYSIS_DIR
                        Directory to write out the chat response when the answer was "unsure" or "unknown"
```