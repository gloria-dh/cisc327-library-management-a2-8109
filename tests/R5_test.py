import pytest, database
from services.library_service import (
    calculate_late_fee_for_book
)
from datetime import datetime, timedelta

#---------------------------------------------------------------------------------------------------------
# New examples - should FAIL pytest because function is not implemented/ missing from library_service.py
#---------------------------------------------------------------------------------------------------------

def test_calculate_late_fee_valid_input_5_days_overdue():
    """Test returning a book with valid input."""

    # vars
    isbn = "2000000000000"
    total_copies = 1
    avail_copies = 1
    patron_id = "200000"

    # add book to database
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id, book["id"], (datetime.now() - timedelta(days=5 + 14)), (datetime.now() - timedelta(days=5)))

    # update book availability
    assert database.update_book_availability(book["id"], -1)

    # calculate the late fee
    res = calculate_late_fee_for_book(patron_id, book["id"])

    # validate return
    assert res["days_overdue"] == 5
    assert res["fee_amount"] == 5*0.50
    assert "overdue" in res["status"].lower()

def test_calculate_late_fee_valid_input_9_days_overdue():
    """Test returning a book with valid input."""

    # vars
    isbn = "0200000000000"
    total_copies = 1
    avail_copies = 1
    patron_id = "020000"

    # add book to database
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id, book["id"], (datetime.now() - timedelta(days=9 + 14)), (datetime.now() - timedelta(days=9)))

    # update book availability
    assert database.update_book_availability(book["id"], -1)

    # calculate the late fee
    res = calculate_late_fee_for_book(patron_id, book["id"])

    # validate return
    assert res["days_overdue"] == 9
    assert res["fee_amount"] == 7*0.50 + 2*1
    assert "overdue" in res["status"].lower()

def test_calculate_late_fee_valid_input_20_days_overdue():
    """Test returning a book with valid input."""

    # vars
    isbn = "0020000000000"
    total_copies = 1
    avail_copies = 1
    patron_id = "002000"

    # add book to database
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id, book["id"], (datetime.now() - timedelta(days=20 + 14)), (datetime.now() - timedelta(days=20)))

    # update book availability
    assert database.update_book_availability(book["id"], -1)

    # calculate the late fee
    res = calculate_late_fee_for_book(patron_id, book["id"])

    # validate return
    assert res["days_overdue"] == 20
    assert res["fee_amount"] == 15.00
    assert "overdue" in res["status"].lower()

def test_calculate_late_fee_valid_input_not_overdue():
    """Test returning a book with valid input."""

    # vars
    isbn = "0002000000000"
    total_copies = 1
    avail_copies = 1
    patron_id = "000200"

    # add book to database
    assert database.insert_book("Test Book R3", "Test Author", isbn, total_copies, avail_copies)

    # get book id
    book = database.get_book_by_isbn(isbn)
    assert book is not None
    assert "id" in book

    # borrow book
    assert database.insert_borrow_record(patron_id, book["id"], datetime.now(), (datetime.now() + timedelta(days=14)))

    # update book availability
    assert database.update_book_availability(book["id"], -1)

    # calculate the late fee
    res = calculate_late_fee_for_book(patron_id, book["id"])

    # validate return
    assert res["days_overdue"] == 0
    assert res["fee_amount"] == 0
    assert "not overdue" in res["status"].lower()
