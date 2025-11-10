"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, 
    get_patron_borrowed_books # GD ADDED
)
from services.payment_service import PaymentGateway

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isbn.isdigit(): # GD ADDED
        return False, "ISBN must contain only digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5: # GD ADDED
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]: # GD ADDED whole function
    """
    Allow a patron to return a book.
    Implements R4 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """

    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists
    book_info = get_book_by_id(book_id)
    if not book_info:
        return False, "Book not found."
    
    borrowed_book_list = get_patron_borrowed_books(patron_id)
    if not borrowed_book_list:
        return False, "no book found borrowed with patron ID"
    
    # check if patron has the specific book borrowed
    for b in borrowed_book_list:
        if b.get("book_id") == book_id:
            break
    else: 
        return False, "no book found borrowed with patron ID"

    # update the borrow record
    update_borrow_record_success = update_borrow_record_return_date(patron_id, book_id, datetime.now())
    if not update_borrow_record_success:
        return False, "Database error occurred with updating borrow record."
    
    # Increment availability
    availability_success = update_book_availability(book_id, +1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."

    return True, f'Successfully returned "{book_info["title"]}"'

# GD ADDED daily fee helper function
DAILY_FEE_FIRST_7 = 0.50
DAILY_FEE_AFTER_7 = 1.00
MAX_LATE_FEE     = 15.00

def find_late_fee(days_overdue: int) -> float:
    if days_overdue <= 0:
        return 0.0
    first_part = min(days_overdue, 7) * DAILY_FEE_FIRST_7
    second_part = max(days_overdue - 7, 0) * DAILY_FEE_AFTER_7
    return float(min(first_part + second_part, MAX_LATE_FEE))


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict: # GD ADDED whole function
    """
    Calculate late fees for a specific book.
    Implements R5 as per requirements 

    input:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow

    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            "fee_amount": 0.00,
            "days_overdue": 0,
            "status": "Invalid patron ID"
        }
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return {
            "fee_amount": 0.00,
            "days_overdue": 0,
            "status": "Book not found."
        }
    
    borrowed_book_list = get_patron_borrowed_books(patron_id)

    if not borrowed_book_list:
        return {
            "fee_amount": 0.00,
            "days_overdue": 0,
            "status": "no book found borrowed with patron ID"
        }
    
    # check if patron has the specific book borrowed
    for book in borrowed_book_list:
        if book.get("book_id") == book_id:
            borrowed_book = book
            break
    else: 
        return {
            "fee_amount": 0.00,
            "days_overdue": 0,
            "status": "no book found borrowed with patron ID"
        }
    
    # Calculate time overdue
    time_now = datetime.now().date()
    due_date = borrowed_book.get("due_date")
    
    # ensure both are date objects
    if isinstance(due_date, datetime):
        due_date = due_date.date()

    days_overdue = max(0, (time_now - due_date).days)

    late_fee = find_late_fee(days_overdue)

    return {
        "fee_amount": late_fee, 
        "days_overdue": int(days_overdue), 
        "status": "Overdue" if days_overdue > 0 else "Not overdue"
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]: # GD ADDED whole function
    """
    Search for books in the catalog.
    Implements R6 as per requirements
    """

    # check input type validity
    if not isinstance(search_term, str) or not isinstance(search_type, str):
        return []
    
    term = search_term.strip().lower()
    stype = search_type.strip().lower()
    if not term:
        return []
    
    books = get_all_books()
    results = []

    # filter results based on search type
    if stype == "title":
        results = [b for b in books if term in (b.get("title")).lower()]
    elif stype == 'author':
        results = [b for b in books if term in (b.get("author")).lower()]
    elif stype == 'isbn':
        results = [b for b in books if term in (b.get("isbn")).lower()]
    
    return results

def get_patron_status_report(patron_id: str) -> Dict: # GD ADDED whole function
    """
    Get status report for a patron.
    Implement R7 as per requirements

    input:
        patron_id: 6-digit library card ID

    return { 
        'currently_borrowed': [{'title': "book 1", 'author': "Steve", 'due_date': "2025/09/18"}, {'title': "book 2", ..., ..., ...}],
        'total_late_fees': 0,
        'num_borrowed_books': 2,
        'borrowing_history': {book 1, book 2}
        }
    """

    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return None

    borrowed_book_list = get_patron_borrowed_books(patron_id)
    if not borrowed_book_list:
        return None
    
    currently_borrowed = []
    time_now = datetime.now().date()
    total_fee = 0.0
    borrowing_history_titles = set()

    for book in borrowed_book_list:
        current = get_book_by_id(book.get("book_id"))

        title = current.get("title")
        author = current.get("author")
        due_date_datetime = book.get("due_date")

        # ensure both are date objects
        if isinstance(due_date_datetime, datetime):
            due_date = due_date_datetime.date()
        else:
            due_date = due_date_datetime

        # Calculate total late fee
        if due_date is None:
            days_overdue = 0
        else:
            days_overdue = max(0, (time_now - due_date).days)
            
        late_fee = find_late_fee(days_overdue)
        total_fee += late_fee

        currently_borrowed.append({
            "title": title,
            "author": author,
            "due_date": due_date_datetime,
        })
        borrowing_history_titles.add(title)

    entry = {
        "currently_borrowed": currently_borrowed,
        "total_late_fees": total_fee,
        "num_borrowed_books": len(currently_borrowed),
        "borrowing_history": borrowing_history_titles,
    }

    return entry

# TASK 2.1 
def pay_late_fees(patron_id: str, book_id: int, payment_gateway: PaymentGateway | None = None) -> Tuple[bool, str]:

    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    all_fee_info = calculate_late_fee_for_book(patron_id, book_id)
    fee = float(all_fee_info.get("fee_amount", 0.0)) # return 0 if missing fee info

    if fee <= 0:
        return False, "No fee due."
    
    # Call gateway is there's a fee due
    gateway = payment_gateway or PaymentGateway()

    try:
        success, txn_id, msg = gateway.process_payment(patron_id, fee, "Late fees")
    except Exception:
        return False, "Error processing payment."
    
    if success:
        return True, f"Payment succesful. ID: {txn_id}."
    else:
        return False, f"Payment failed. Message: {msg}."
    
def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway: PaymentGateway | None = None) -> Tuple[bool, str]:

    # Validate transaction ID
    if not transaction_id or not transaction_id.startswith("txn_"):
        return False, "Invalid transaction ID."
    
    # Validate refund amount
    if not(0 < amount <= 15.0):
        return False, "Invalid refund amount. Must be between $0 and $15."
    
    # Call gateway
    gateway = payment_gateway or PaymentGateway()

    try:
        success, msg = gateway.refund_payment(transaction_id, amount)
    except Exception:
        return False, "Error processing refund."
    
    if success:
        return True, f"Refund successful. Message: {msg}."
    else:
        return False, f"Refund failed. Message: {msg}."


