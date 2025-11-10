import pytest, database
from services.library_service import (
    borrow_book_by_patron
)

#---------------------------------------------------------------------------------------------------------
# New examples - PASS pytest
#---------------------------------------------------------------------------------------------------------

def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""

    # vars
    isbn = "6666666666666"
    total_copies = 1
    avail_copies = 1
    patron_id = "000000"

    # insert book to borrow
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # find book id from isbn
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    success2, message2 = borrow_book_by_patron(patron_id, book["id"])
    assert success2 == True
    assert "successfully borrowed" in message2.lower()

def test_borrow_book_invalid_patron_id_with_letters():
    """Test borrowing a book with a non-numerical patron ID."""
    # vars
    isbn = "7777777777777"
    total_copies = 1
    avail_copies = 1
    patron_id = "ABC456"

    # insert book to borrow
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # find book id from isbn
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book with invalid patron ID
    success2, message2 = borrow_book_by_patron(patron_id, book["id"])
    assert success2 == False
    assert "invalid patron id" in message2.lower()

def test_borrow_book_invalid_patron_id_more_than_six_digits():
    """Test borrowing a book with a patron ID larger than 6 digits."""

    # vars
    isbn = "8888888888888"
    total_copies = 1
    avail_copies = 1
    patron_id = "1234567"

    # insert book to borrow
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # find book id from isbn
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book with patron ID longer than 6 digits
    success2, message2 = borrow_book_by_patron(patron_id, book["id"])
    assert success2 == False
    assert "invalid patron id" in message2.lower()

#---------------------------------------------------------------------------------------------------------
# New example - should FAIL pytest because function is not implemented/ missing from library_service.py
#---------------------------------------------------------------------------------------------------------

def test_borrow_book_invalid_borrow_more_than_five_books():
    """Test borrowing more than 5 books."""
    # vars
    isbn = "9999999999999"
    total_copies = 6
    avail_copies = 6
    patron_id = "111111"

    # insert book to borrow
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # find book id from isbn
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow 5 books - should have no problem
    for i in range(5):
        success2, message2 = borrow_book_by_patron(patron_id, book["id"])
        assert success2 == True
        assert "successfully borrowed" in message2.lower()

    # borrow a 6th book - should error because of limit
    for i in range(avail_copies - 5):
        success3, message3 = borrow_book_by_patron(patron_id, book["id"])
        assert success3 == False
        assert "limit of 5 books" in message3.lower()