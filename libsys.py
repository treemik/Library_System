from helper_functions import init_db, DatabaseContextManager
from datetime import datetime
import sqlite3
import argparse

#set up parser
parser = argparse.ArgumentParser(description="A cli library system that adds books tracks loans and members")
subparsers = parser.add_subparsers(dest="command")
subparsers.required = True
# add subparser add book
add_parser = subparsers.add_parser("add_book", help="Add a book track")
add_parser.add_argument("-t","--title",required=True, help="The title of the book")
add_parser.add_argument("-a","--author",required=True, help="The author of the book")
add_parser.add_argument("-p","--published",help="The published date of the book")
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

init_db()

if args.command=="add_book":
    with DatabaseContextManager("library.db") as conn:
        cursor = conn.cursor()
        created_at=datetime.now().strftime("%Y-%m-%d")
        normalized_name=" ".join(args.author.strip().split()).lower()
        if not args.published:
            pub_year=None
        else:
            pub_year=int(args.published)
        if not args.isbn:
            isbn=None
        else:
            isbn=args.isbn
        cursor.execute(
            "INSERT INTO titles (title,pub_year,isbn,created_at)VALUES(?,?,?,?)",
            (args.title,pub_year,isbn,created_at)
        )
        tit_id=cursor.lastrowid
        cursor.execute(
            "INSERT INTO authors(full_name,normalized_name)VALUES(?,?) ON CONFLICT (normalized_name) DO UPDATE SET full_name=excluded.full_name",
            (args.author,normalized_name)
        )
        aut_id=cursor.execute("SELECT id FROM authors WHERE normalized_name=?",(normalized_name,)).fetchone()[0]

        cursor.execute(
            "INSERT INTO title_authors(title_id,author_id,author_order)VALUES(?,?,?)",
            (tit_id,aut_id,1)
        )









