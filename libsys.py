#import required library's
from helper_functions import init_db, DatabaseContextManager, published_type, isbn_type, email_type, phone_type
from services import add_book, add_author, add_member, search_book, search_member
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
add_parser.add_argument("-e","--email",type=email_type,required=True,help="The email address of the member")
add_parser.add_argument("-p","--phone",type=phone_type,help="The phone number of the member")
# add subparser search book
add_parser=subparsers.add_parser("search_book", help="Search for a title")
add_parser.add_argument("-t","--title",required=True,help="The title of the book")
# add subparser search member
add_parser=subparsers.add_parser("search_member", help="Search for a member")
add_parser.add_argument("-e","--email",type=email_type,help="search by email")
add_parser.add_argument("-p","--phone",type=phone_type,help="search by phone")
add_parser.add_argument("-n","--name",help="search by name")



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
        book_id,book_title=add_book(conn,title=title,authors=authors,pub_year=pub_year,isbn=isbn)
        print (f"{book_title} was added with id {book_id}")

#handle add author
elif args.command=="add_author":
    with DatabaseContextManager("library.db") as conn:
        cursor=conn.cursor()
        first=args.first.strip()
        last=args.last.strip()
        author_id, display_name=add_author(conn,first=first,last=last)
        print (f'Author {display_name} Added/Reused with the id {author_id}')

elif args.command=="add_member":
    with DatabaseContextManager("library.db") as conn:
        first=args.first.strip().capitalize()
        last=args.last.strip().capitalize()
        email=args.email
        phone=args.phone
        result=add_member(conn,first=first,last=last,email=email,phone=phone)
        if result is None:
            print (f"Email {email} already exists")
        else:
            member_id,full_name=result
            print(f'Member {full_name} was added with the id {member_id}')

elif args.command=="search_book":
    with DatabaseContextManager("library.db") as conn:
        title=args.title.strip().lower()
        results=search_book(conn,title=title)
        if results is None:
            print (f"Title {title} was not found")
        else:
            print (f"\nResults for the title {title} \n")
            print ("-"*47)
            print (f"{'ID':<4} | {'Title':<16} | {'Available':<9} | {'Total':<9}")
            print ("-"*47)
            for result in results:
                book_id=result["id"]
                book_title=result["title"]
                available=result["available"]
                total=result["total"]
                print (f"{book_id:<4} | {book_title[:15]:<16} | {available:<9} | {total:<9}")

elif args.command=="search_member":
    with DatabaseContextManager("library.db") as conn:
        name=args.name.strip().lower()
        results=search_member(conn,email=args.email,name=name,phone=args.phone)
        search_params=[]
        if args.email:
            search_params.append(args.email)
        if args.phone:
            search_params.append(args.phone)
        if args.name:
            search_params.append(args.name)
        search_string=" ".join(search_params)

        if not results:
            print (f"No results found for {search_string}")
        else:
            print (f"\n Results for {search_string} \n")
            print ("-"*65)
            print (f"{'ID':<4} | {'Member name':<16} | {'Member Phone':<13} | {'Member Email'}")
            print ("-"*65)
            for result in results:
                member_id=result["id"]
                member_name=result["name"]
                member_phone=result["phone"]
                member_email=result["email"]
                print (f"{member_id:<4} | {member_name[:15]:<16} | {member_phone:<13} | {member_email}")

















