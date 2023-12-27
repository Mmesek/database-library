import re, csv, datetime

from argparse import ArgumentParser
from email.utils import parsedate_to_datetime
from email.header import decode_header, make_header
from mailbox import mbox

parser = ArgumentParser()
parser.add_argument("-i", "--inbox", default="INBOX", help="Mailbox file")
parser.add_argument("-o", "--output", default="bazar.csv", help="Output csv")
parser.add_argument("-f", "--sender", default="Bazar <bazar@lowcygier.pl>", help="Search only from this sender")
parser.add_argument("-s", "--subject", default="zarezerwowano", help="Search if keyword in subject")
parser.add_argument(
    "-p",
    "--pattern",
    default=r"Bazar - zarezerwowano Twoją grę (.*) za (\d+,\d+) zł",
    help="Pattern to match title and price from subject",
)

args = parser.parse_args()

INBOX = args.inbox
OUTPUT = args.output
FROM = args.sender
SUBJECT = args.subject
PATTERN = re.compile(args.pattern)


def parse_mail(msg: dict[str, str]) -> tuple[datetime.datetime, str, str]:
    if msg.get("from") == FROM and SUBJECT in msg.get("subject"):
        subject = str(make_header(decode_header(msg.get("subject").strip().replace("\n", ""))))
        date = parsedate_to_datetime(msg.get("date"))
        title, prc = PATTERN.match(subject).groups()
        return (date, title, prc.replace(",", "."))


if __name__ == "__main__":
    msgs = []
    for msg in mbox(INBOX).itervalues():
        msgs.append(parse_mail(msg))

    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        f = csv.writer(file)
        f.writerows(msgs)
