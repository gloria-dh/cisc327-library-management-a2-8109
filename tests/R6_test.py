import pytest, database
from services.library_service import (
    search_books_in_catalog
)

#---------------------------------------------------------------------------------------------------------
# New examples - should FAIL pytest because function is not implemented/ missing from library_service.py
#---------------------------------------------------------------------------------------------------------

def test_search_books_valid_title():
    # vars
    isbn = "3000000000000"
    total_copies = 1
    avail_copies = 1
    search_term = "Test Book R6"
    search_type = "title"

    # add book to database
    assert database.insert_book("Test Book R6", "Test Author", isbn, total_copies, avail_copies)

    # search book title
    book_list = search_books_in_catalog(search_term, search_type)
    assert book_list is not None
    assert len(book_list) >= 1

def test_search_books_valid_author():
    # vars
    isbn = "0300000000000"
    total_copies = 1
    avail_copies = 1
    search_term = "Test Author"
    search_type = "author"

    # add book to database
    assert database.insert_book("Test Book R6", "Test Author", isbn, total_copies, avail_copies)

    # search book title
    book_list = search_books_in_catalog(search_term, search_type)
    assert book_list is not None
    assert len(book_list) >= 1

def test_search_books_valid_isbn():
    # vars
    isbn = "0030000000000"
    total_copies = 1
    avail_copies = 1
    search_term = isbn
    search_type = "isbn"

    # add book to database
    assert database.insert_book("Test Book R6", "Test Author", isbn, total_copies, avail_copies)

    # search book title
    book_list = search_books_in_catalog(search_term, search_type)
    assert book_list is not None
    assert len(book_list) >= 1

    # look through list of books to see if mathcing isbn is found
    res = False
    for book in book_list:
        if book.get("isbn") == isbn:
            res = True
            break
    assert res == True

def test_search_books_invalid_isbn():
    # vars
    isbn = "0003000000000"
    total_copies = 1
    avail_copies = 1
    search_term = "0000300000000"
    search_type = "isbn"

    # add book to database
    assert database.insert_book("Test Book R6", "Test Author", isbn, total_copies, avail_copies)

    # search book title
    book_list = search_books_in_catalog(search_term, search_type)
    assert book_list == []

    # look through list of books to see if mathcing isbn is found
    res = False
    for book in book_list:
        if book.get("isbn") == isbn:
            res = True
            break
    assert res == False


