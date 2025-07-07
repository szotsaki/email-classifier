import argparse

from classifier.Classifier import Classifier
from classifier.Email import Email
from classifier.Model import Model
from classifier.SocketListener import UnixSocketListener


def classify(args, email_content: bytes) -> bytes:
    model = Model(args.model)
    email_structure = Email(email_content).parse()
    classification = Classifier(email_structure).classify(model)

    ret = classification if classification else "error"
    return ret.encode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='E-mail classifier')
    parser.add_argument('-s', '--socket', type=str,
                        help='UNIX socket path to listen on incoming e-mails. Default: /run/email-classifier/classify.sock',
                        default="/run/email-classifier/classify.sock")
    parser.add_argument('--socket-uid', help='UID (user id) of the created UNIX socket', default=-1)
    parser.add_argument('--socket-gid', help='GID (group id) of the created UNIX socket', default=-1)
    parser.add_argument('--max-size', type=int,
                        help='Maximum size (in bytes) of an e-mail to be processed. Default: 30 MiB',
                        default=1024 * 1024 * 30)
    parser.add_argument('-t', '--timeout', type=int,
                        help='Timeout (in seconds) for an e-mail to arrive through the socket. Default: 10 seconds',
                        default=10)
    parser.add_argument('-m', '--model', type=str,
                        help='Model to use for classification. Default: mistral:7b',
                        default="mistral:7b")
    args = parser.parse_args()

    classify_bound = lambda email_content: classify(args, email_content)
    listener = UnixSocketListener(args.socket, args.socket_uid, args.socket_gid, args.timeout, args.max_size,
                                  classify_bound)
    listener.listen()
