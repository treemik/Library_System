from helper_functions import init_db, DatabaseContextManager
from services import add_book
import re
from datetime import datetime

import argparse
#year regex
year_re=re.compile(r"^\s*(\d{4})(?:-(\d{2})(?:-\d{2})?)?\s*$")
def published_type(s: str)->int:
    match = year_re.match(s)
    if not match:
        raise argparse.ArgumentTypeError(f"{s} is not a valid date please enter a vaild date (YYYY-MM-DD OR YYYY-MM OR YYYY)")
    year = int(match.group(1))
    now = int(datetime.now().year)
    if not 1400 <= year <= now+1:
        raise argparse.ArgumentTypeError(f"{year} is not a valid year")
    return year


#set up parser
parser = argparse.ArgumentParser(description="A cli library system that adds books tracks loans and members")
subparsers = parser.add_subparsers(dest="command")
subparsers.required = True
# add subparser add book
add_parser = subparsers.add_parser("add_book", help="Add a book track")
add_parser.add_argument("-t","--title",required=True, help="The title of the book")
add_parser.add_argument("-a","--author",required=True, action="append", help="The author of the book")
add_parser.add_argument("-p","--published",type=published_type,help="The published date of the book")
add_parser.add_argument("--isbn", help="The ISBN of the book")
# add subparser add author
add_parser=subparsers.add_parser("add_author", help="Add an author")
add_parser.add_argument("-f","--first",required=True, help="The first name of the author")
add_parser.add_argument("-l","--last",required=True, help="The last name of the author")
# add subparser add members
add_parser=subparsers.add_parser("add_member", help="Add a member")
add_parser.add_argument("-f","--first",required=True,help="Members first name")
add_parser.add_argument("-l","--last",required=True,help="Members last name")
add_parser.add_argument("-e","--email",required=True,help="The email address of the member")
add_parser.add_argument("-p","--phone",help="The phone number of the member")

args = parser.parse_args()
#Initilize the database
init_db()
#handle add book
if args.command=="add_book":
    with DatabaseContextManager("library.db") as conn:

        if not args.published:
            pub_year=None
        else:
            pub_year=(args.published)
        if not args.isbn:
            isbn=None
        else:
            isbn=args.isbn
        title = args.title
        authors = args.author

        add_book(conn,title=title,authors=authors,pub_year=pub_year,isbn=isbn)











