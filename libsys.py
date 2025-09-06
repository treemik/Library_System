#import required library's
from helper_functions import init_db, DatabaseContextManager, published_type, isbn_type, normalize_and_dedupe
from services import add_book
import argparse


#set up parser
parser = argparse.ArgumentParser(description="A cli library system that adds books tracks loans and members")
subparsers = parser.add_subparsers(dest="command")
subparsers.required = True
# add subparser add book
add_parser = subparsers.add_parser("add_book", help="Add a book track")
add_parser.add_argument("-t","--title",required=True, help="The title of the book")
add_parser.add_argument("-a","--author",required=True, action="append", help="The author of the book")
add_parser.add_argument("-p","--published",type=published_type,help="The published date of the book")
add_parser.add_argument("--isbn",type= isbn_type,help="The ISBN of the book")
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
        isbn = args.isbn
        title = args.title
        authors = args.author
        pub_year = args.published
        add_book(conn,title=title,authors=authors,pub_year=pub_year,isbn=isbn)

#handle add author
elif args.command=="add_author":
    with DatabaseContextManager("library.db") as conn:
        cursor=conn.cursor()
        full_name=" ".join([args.first.strip(), args.last.strip()])
        pair=normalize_and_dedupe([full_name])
        display,normalized=pair[0]
        cursor.execute(
            "INSERT INTO authors(full_name,normalized_name)VALUES(?,?) ON CONFLICT (normalized_name) DO UPDATE SET full_name=excluded.full_name",
            (display, normalized)
        )
        aut_id = cursor.execute("SELECT id FROM authors WHERE normalized_name=?", (normalized,)).fetchone()[0]













