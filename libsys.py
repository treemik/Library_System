

from helper_functions import init_db, DatabaseContextManager, published_type, isbn_type, email_type, phone_type, quantity_type
from services import add_book, add_author, add_member, search_book, search_member, add_copy, loan_book, return_book,search_loan, check_overdue_loans,lost_or_withdrawn, change_member_status,renew
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
# Add subparser add copy
add_parser=subparsers.add_parser("add_copy", help="add a copy")
add_parser.add_argument('--id',type=int,required=True,help="The id of the copy")
add_parser.add_argument('-q','--quantity',type=quantity_type,help="The quantity of the copies",default=1)
# Add subparser loan
add_parser=subparsers.add_parser("loan", help="loan a book")
add_parser.add_argument('--id',type=int,required=True,help="The id of the book")
add_parser.add_argument('--member_id',type=int,required=True,help="The id of the member")
add_parser.add_argument('-d','--days', type=int,help='length of the loan in days' ,default=14)
# Add subparser return_book:
add_parser=subparsers.add_parser("return_book", help="return a book")
add_parser.add_argument('--loan_id',type=int,required=True,help="The id of the loan")
# add subparser search_loan
add_parser=subparsers.add_parser("search_loan", help="search for a loan")
add_parser.add_argument('-m','--mid',type=int,help="The members id")
add_parser.add_argument('--tid',type=int,help='the title id')
# Add subparser overdue
add_parser=subparsers.add_parser("overdue", help="cheak overdue loans")
#Add subparser status_update
add_parser=subparsers.add_parser("status_update", help="update the status of a book")
add_parser.add_argument('--id',type=int,required=True,help="The id of the book")
add_parser.add_argument('--status',type=str.lower,choices=["lost","withdrawn"],help="The status of the book",required=True)
#Add parser member_status
add_parser=subparsers.add_parser("member_status",help="change members status")
add_parser.add_argument('--id',type=int,required=True,help="The id of the member")
add_parser.add_argument('--status',type=int,choices=[1,0],required=True,help="The status of the member must be 1 active or 0 inactive")\
#add subparser renew
add_parser=subparsers.add_parser("renew",help="renew the status of a book")
add_parser.add_argument('--id',type=int,required=True,help="The id of the book")



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
        name = None
        if args.name:
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

elif args.command=="add_copy":
    with DatabaseContextManager("library.db") as conn:
        title_id,quantity=add_copy(conn,book_id=args.id,quantity=args.quantity)
        if quantity== 0:
            print (f"\nNo book found with the ID:{title_id}\n")
        elif quantity==1:
            print(f"\n{quantity} copy of the book with ID:{title_id} was added\n")
        else:
            print(f"\n{quantity} copies of the book with ID:{title_id} were added\n")

elif args.command=="loan":
    with DatabaseContextManager("library.db") as conn:
        results=loan_book(conn,title_id=args.id,member_id=args.member_id,days=args.days)
        if not results['ok']:
            err=results['error']
            if err=="NO_SUCH_TITLE":
                print(f"No book found with the ID:{args.id}")
            elif err=="NO_SUCH_MEMBER":
                print(f"No member found with the ID:{args.member_id}")
            elif err=='NO_COPIES_AVAILABLE':
                print(f"No copies available for the book with ID:{args.id}")
            elif err=='RACE_LOST':
                print(f"Copy was claimed by another loan. Try again")
            elif err=='DB_ERROR':
                print(f"Database error. Try again")

        else:
            loan = results['data']
            print(f"\n Book {loan['title_id']} was loaned to member {loan['member_id']} loan id: {loan['loan_id']}\n loaned on {loan['loaned_at']} due {loan['due']} ")

elif args.command=="return_book":

    with DatabaseContextManager("library.db") as conn:
        results=return_book(conn,loan_id=args.loan_id)
        if not results['ok']:
            err=results['error']
            if err=="NO_SUCH_LOAN":
                print(f"No book found with the ID:{args.loan_id}")
            elif err=="ALREADY_RETURNED":
                print(f"This loan was returned {results['returned_at']}")
        else:
            returned=results['data']
            print (f"The loan {args.loan_id} for the copy {returned['copy_id']} was returned {returned['return_date']}")

elif args.command=='search_loan':
    with DatabaseContextManager("library.db") as conn:
        results=search_loan(conn,member_id=args.mid,title_id=args.tid)
        if not results['ok']:
            err=results['error']
            if err=="MEMBER_HAS_NO_LOANS":
                print(f"No loans found with the ID:{args.mid}")
            if err=="TITLE_NOT_ON_LOAN":
                print (f"No copies with the tile id:{args.tid} are on loan")
            if err=="NO_COPIES_ON_LOAN":
                print(f"No copies with the tile id:{args.tid} are on loan")

        else:
            loan = results['data']
            for loan_id in loan:
                print (f"the loan ids for the search are {loan_id}")

elif args.command=="overdue":
    with DatabaseContextManager("library.db") as conn:
        results=check_overdue_loans(conn)
        if not results['ok']:
            err=results['error']
            if err=="NO_ACTIVE_LOANS":
                print("\nThere are no active loans")
        else:
            overdue=results['data']
            if not overdue:
                print("\nThere are no overdue loans\n")
            else:
                print("\n")
                print("-" * 60)
                print("Currently overdue loans")
                print("-" * 60)
                print(f"\n{'loan_id':<7} | {'copy_id':<7} | {'member_id':<9} | {'loaned_at':<10} | {'due_at':<10}")
                for loan in overdue:
                    loan_id = loan['loan_id']
                    copy_id = loan['copy_id']
                    member_id = loan['member_id']
                    loaned_at = loan['loaned_at']
                    due_at = loan['due_at']
                    print (f"{loan_id:<7} | {copy_id:<7} | {member_id:<9} | {loaned_at:<10} | {due_at:<10}")
                print("\n")

elif args.command=="status_update":
    with DatabaseContextManager("library.db") as conn:
        results=lost_or_withdrawn(conn,copy_id=args.id,status=args.status)
        if not results['ok']:
            err=results['error']
            if err=="NO_SUCH_COPY":
                print(f"there are no copies with the id {args.id}")


        else:
            print(f"the copy with the id: {args.id} status updated to {args.status}")


elif args.command=="member_status":
    with DatabaseContextManager("library.db") as conn:
        if args.status==1:
            status="active"
        else:
            status="inactive"
        results=change_member_status(conn,member_id=args.id,status=args.status)
        if not results['ok']:
            err=results['error']
            if err=="NO_SUCH_MEMBER":
                print(f"there are no members with the id {args.id}")
        else:
            print(f"The member with the id: {args.id} status updated to {status}")

elif args.command=="renew":
    with DatabaseContextManager("library.db") as conn:
        results=renew(conn,copy_id=args.id)
        if not results['ok']:
            err=results['error']
            if err=="NO_ACTIVE_LOAN_FOR_COPY":
                print(f"there are no copies with the id {args.id}")
        else:
            print(f"the copy with the id: {args.id} renewed")




















