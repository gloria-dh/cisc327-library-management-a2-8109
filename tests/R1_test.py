import pytest
from services.library_service import (
    add_book_to_catalog
)

# add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str], Returns: tuple: (success: bool, message: str)

#---------------------------------------------------------------------------------------------------------
# Assignment provided examples - PASS pytest
#---------------------------------------------------------------------------------------------------------

def test_add_book_valid_input():
    """Test adding a book with valid input."""

    #vars
    isbn = "1234567890123"
    total_copies = 5

    # add book to catalog
    success, message = add_book_to_catalog("Test Book", "Test Author", isbn, total_copies)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""

    # vars
    isbn = "123456789"
    total_copies = 5

    # add book with ibsn too short
    success, message = add_book_to_catalog("Test Book", "Test Author", isbn, total_copies)
    
    assert success == False
    assert "13 digits" in message

# Add more test methods for each function and edge case. You can keep all your test in a separate folder named `tests`.

#---------------------------------------------------------------------------------------------------------
# New examples - PASS pytest
#---------------------------------------------------------------------------------------------------------

def test_add_book_invalid_isbn_too_long():
    """Test adding a book with ISBN too long."""

    # vars
    isbn = "33333333333333"
    total_copies = 5

    # add book with isbn too long
    success, message = add_book_to_catalog("Test Book", "Test Author", isbn, total_copies)

    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_total_copies_negative_input():
    """Test adding a book with negative number for total copies."""

    # vars
    isbn = "1111111111111"
    total_copies = -5

    # add book with negative value for total copeis
    success, message = add_book_to_catalog("Test Book", "Test Author", isbn, total_copies)

    assert success == False
    assert "positive integer" in message

def test_add_book_invalid_title_more_than_two_hundred_char():
    """Test adding a book with a title longer than 200 characters."""

    # vars
    isbn = "2222222222222"
    total_copies = 5

    # add book with a title longer than 200 characters
    success, message = add_book_to_catalog("A"*201, "Test Author", isbn, total_copies)

    assert success == False
    assert ("title" in message.lower()) and ("less than 200" in message)

def test_add_book_invalid_author_more_than_one_hundred_char():
    """Test adding a book with an author name longer than 100 characters."""

    # vars
    isbn = "4444444444444"
    total_copies = 5

    # add book with an author name with more than 100 characters
    success, message = add_book_to_catalog("Test Book", "B"*101, isbn, total_copies)

    assert success == False
    assert ("author" in message.lower()) and ("less than 100" in message)

def test_add_book_invalid_missing_title_input():
    """Test adding a book with no input for title."""

    # vars
    isbn = "5555555555555"
    total_copies = 5

    # add book with missing title
    success, message = add_book_to_catalog("", "Test Author", isbn, total_copies)

    assert success == False
    assert "title is required" in message.lower()

#---------------------------------------------------------------------------------------------------------
# New example - should FAIL pytest because function is not implemented/ missing from library_service.py
#---------------------------------------------------------------------------------------------------------

def test_add_book_invalid_isbn_with_letters():
    """Test adding a book with ISBN with non-numerical input."""

    # vars
    isbn = "ABC4567890123"
    total_copies = 5

    # add book with an isbn containing letters
    success, message = add_book_to_catalog("Test Book", "Test Author", isbn, total_copies)

    assert success == False
    assert ("only digits" in message.lower()) or ("database error" in message.lower())
