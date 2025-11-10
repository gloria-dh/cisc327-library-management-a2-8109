import pytest, database
from services.library_service import (
    return_book_by_patron
)
from datetime import datetime, timedelta

#---------------------------------------------------------------------------------------------------------
# New examples - should FAIL pytest because function is not implemented/ missing from library_service.py
#---------------------------------------------------------------------------------------------------------

def test_return_book_valid_input():
    """Test returning a book with valid input."""

    # vars
    isbn = "1000000000000"
    total_copies = 1
    avail_copies = 1
    patron_id = "100000"

    # add book to database
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id, book["id"], datetime.now(), (datetime.now() + timedelta(days=14)))

    # update book availabilty in database
    assert database.update_book_availability(book["id"], -1)

    # return book
    success3, message3 = return_book_by_patron(patron_id, book["id"])
    assert success3 == True
    #assert "successfully returned" in message3.lower()

def test_return_book_invalid_not_borrowed_by_patron():
    """Test returning a book that was not checked out by the patron ID."""

    # vars
    isbn = "0100000000000"
    total_copies = 1
    avail_copies = 1
    patron_id_one = "010000"
    patron_id_two = "001000"

    # add book to database
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id_one, book["id"], datetime.now(), (datetime.now() + timedelta(days=14)))

    # update book availabilty in database
    assert database.update_book_availability(book["id"], -1)

    # return book with different patron id
    success3, message3 = return_book_by_patron(patron_id_two, book["id"])
    assert success3 == False
    assert not ("book return functionality is not yet implemented." in message3.lower()) and ("no book found" in message3.lower())

def test_return_book_invalid_book_id_not_found():
    """Test returning a book with an invalid book ID"""

     # vars
    isbn = "0010000000000"
    total_copies = 1
    avail_copies = 1
    patron_id = "000100"
    invalid_book_id = "10000000"

    # add book to database
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id, book["id"], datetime.now(), (datetime.now() + timedelta(days=14)))

    # update book availabilty in database
    assert database.update_book_availability(book["id"], -1)
    
    # return book with an invalid book id
    success3, message3 = return_book_by_patron("000100", invalid_book_id)
    assert success3 == False
    assert not ("book return functionality is not yet implemented." in message3.lower()) and ("not found" in message3.lower())


def test_return_book_valid_available_copies_updated():
    """Test that the available copies updated after the user returns a book"""

    # vars
    isbn = "0001000000000"
    total_copies = 3
    avail_copies = 3
    patron_id = "000010"

    # add book to database
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # get book id and available copies
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book
    assert "available_copies" in book

    # find how many availble copies thier are
    before_borrow = database.get_book_by_id(book["id"])["available_copies"]
    assert before_borrow == total_copies

    # borrow book
    assert database.insert_borrow_record(patron_id, book["id"], datetime.now(), (datetime.now() + timedelta(days=14)))

    # update book availabilty in database
    assert database.update_book_availability(book["id"], -1)

    # see how many available copies thier are after borrowing (should be -1)
    after_borrow = database.get_book_by_id(book["id"])["available_copies"]
    assert after_borrow == 2

    # return the book and see if the book count increased by 1
    success3, message3 = return_book_by_patron(patron_id, book["id"])
    assert success3 == True
    assert "successfully returned" in message3.lower()

    # check that the number of books we started with equals the number after the return
    after_return = database.get_book_by_id(book["id"])["available_copies"]
    assert after_return == before_borrow


