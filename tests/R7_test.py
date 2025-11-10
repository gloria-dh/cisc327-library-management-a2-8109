import pytest, database
from services.library_service import (
    get_patron_status_report
)
from datetime import datetime, timedelta

#---------------------------------------------------------------------------------------------------------
# New examples - should FAIL pytest because function is not implemented/ missing from library_service.py
#---------------------------------------------------------------------------------------------------------

# assuming return dictionary format is    key: patron ID 
# 
# return { 
#       'currently_borrowed': [{'title': "book 1", 'author': "Steve", 'due_date': "2025/09/18"}, {'title': "book 2", ..., ..., ...}],
#       'total_late_fees': 0,
#       'num_borrowed_books': 2,
#       'borrowing_history': {book 1, book 2}
#       }

def test_patron_status_valid_id_no_late():

    # vars
    isbn = "4000000000000"
    total_copies = 1
    avail_copies = 1
    patron_id = "400000"
    borrow_date = datetime.now()
    due_date = (datetime.now() + timedelta(days=14))

    # add book to database
    assert database.insert_book("Test Book R7", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id, book["id"], borrow_date, due_date)

    # update book availability
    assert database.update_book_availability(book["id"], -1)

    # get patron status
    status = get_patron_status_report(patron_id)

    # check status
    book_one = status["currently_borrowed"][0]
    assert book_one["title"] == "Test Book R7"
    assert book_one["author"] == "Test Author"
    assert book_one["due_date"] == due_date

    assert status["total_late_fees"] == 0
    assert status["num_borrowed_books"] == 1
    assert status["borrowing_history"] == {"Test Book R7"}


def test_patron_status_invalid_non_exisitent_id():
    # vars
    isbn = "0400000000000"
    total_copies = 1
    avail_copies = 1
    patron_id_one = "040000"
    patron_id_two = "004000"
    borrow_date = datetime.now()
    due_date = (datetime.now() + timedelta(days=14))

    # add book to database
    assert database.insert_book("Test Book R7", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id_one, book["id"], borrow_date, due_date)

    # update book availability
    assert database.update_book_availability(book["id"], -1)

    # get patron status
    status = get_patron_status_report(patron_id_two)

    # check status
    assert status is None

def test_patron_status_valid_invalid_with_letters_id():
    # vars
    isbn = "0040000000000"
    total_copies = 1
    avail_copies = 1
    patron_id_one = "004000"
    patron_id_two = "ABC000"
    borrow_date = datetime.now()
    due_date = (datetime.now() + timedelta(days=14))

    # add book to database
    assert database.insert_book("Test Book R7", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id_one, book["id"], borrow_date, due_date)

    # update book availability
    assert database.update_book_availability(book["id"], -1)

    # get patron status
    status = get_patron_status_report(patron_id_two)

    # check status
    assert status is None

def test_patron_status_valid_id_with_late_5_days():

    # vars
    isbn = "0004000000000"
    total_copies = 1
    avail_copies = 1
    patron_id = "000400"
    borrow_date = (datetime.now() - timedelta(days=5 + 14))
    due_date = (datetime.now() - timedelta(days=5))

    # add book to database
    assert database.insert_book("Test Book R7", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id, book["id"], borrow_date, due_date)

    # update book availability
    assert database.update_book_availability(book["id"], -1)

    # get patron status
    status = get_patron_status_report(patron_id)

    # check status
    book_one = status["currently_borrowed"][0]
    assert book_one["title"] == "Test Book R7"
    assert book_one["author"] == "Test Author"
    assert book_one["due_date"] == due_date

    assert status["total_late_fees"] == 5*0.50
    assert status["num_borrowed_books"] == 1
    assert status["borrowing_history"] == {"Test Book R7"}


#non existent ID -> pass (DONE)
#Valid patron ID w/ late books 5 days-> pass
#Invalid patron ID -> pass (DONE)
#Valid patron ID w/ no late books (DONE)
