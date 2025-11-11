import pytest
from services.payment_service import PaymentGateway
from services import library_service as lib_service
from unittest.mock import Mock

# -------------------- STUBS --------------------
def stub_get_book_by_id(mocker, book_id = 1, title = "A Tale of Two Cities"):
    return mocker.patch.object(
        lib_service, 
        "get_book_by_id",
        autospec = True,
        return_value = {"id": book_id, "title": title, "author": "Author"}
    )

def stub_calc_late_fee(mocker, amount: float, days_overdue = 6, status = None):
    return mocker.patch.object(
        lib_service, 
        "calculate_late_fee_for_book",
        autospec = True,
        return_value = {
            "fee_amount": float(amount),
            "days_overdue": days_overdue,
            "status": status or "Overdue" if amount > 0 else "Not overdue"
        }
    )

## -------------------- pay_late_fees() TESTS --------------------

# successful payment
def test_pay_late_fee_valid(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee(mocker, 3.00) # price for 6 days overdue
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (True, f"txn_{patron_id}_", "processed successfully")
    success, msg, txn = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is True
    assert "Payment successful!" in msg
    assert txn == f"txn_{patron_id}_"
    gateway.process_payment.assert_called_once_with(
        patron_id = patron_id,
        amount = 3.0,
        description = "Late fees for 'A Tale of Two Cities'")

# payment declined by gateway
def test_pay_late_fee_gateway_declined(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee(mocker, 1001.0) # gateway is expected to decline this amount
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (False, "", "Payment declined")
    success, msg, txn = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is False
    assert "Payment failed" in msg
    assert txn is None
    gateway.process_payment.assert_called_once_with(
        patron_id = patron_id, 
        amount = 1001.0, 
        description = "Late fees for 'A Tale of Two Cities'")

# invalid patron ID (verify mock NOT called)
def test_pay_late_fee_invalid_patron_id(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee(mocker, 3.00) # price for 6 days overdue
    patron_id = "ABC777"

    gateway = Mock(spec=PaymentGateway)
    success, msg, txn = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is False
    assert "Invalid patron ID" in msg
    assert txn is None
    gateway.process_payment.assert_not_called()

# zero late fees (verify mock NOT called)
def test_pay_late_fee_zero_fee(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee(mocker, 0.0) # no fee
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    success, msg, txn = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is False
    assert "No late fees to pay for this book" in msg
    assert txn is None
    gateway.process_payment.assert_not_called()

# network error exception handling
def test_pay_late_fee_network_error(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee(mocker, 3.00) # price for 6 days overdue
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.side_effect = Exception("Network Error")
    success, msg, txn = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is False
    assert "Payment processing error" in msg
    assert txn is None
    gateway.process_payment.assert_called_once_with(
        patron_id = patron_id, 
        amount = 3.00, 
        description = "Late fees for 'A Tale of Two Cities'")

## -------------------- refund_late_fee_payment() TESTS --------------------

# succesful refund
def test_refund_late_fee_valid(mocker):
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "processed successfully")
    success, msg = lib_service.refund_late_fee_payment(f"txn_{patron_id}_123", 10.5, payment_gateway = gateway)

    assert success is True
    assert "processed successfully" in msg
    gateway.refund_payment.assert_called_once_with(f"txn_{patron_id}_123", 10.5)

# invalid transaction ID rejection
def test_refund_late_fee_invalid_txn_id(mocker):
    gateway = Mock(spec=PaymentGateway)
    txn_id = "ABC" # invalid txn ID

    success, msg = lib_service.refund_late_fee_payment(txn_id, 10.5, payment_gateway = gateway)

    assert success is False
    assert "Invalid transaction ID" in msg
    gateway.refund_payment.assert_not_called()

# invalid refund amounts (negative, zero, exceeds $15 maximum)
@pytest.mark.parametrize("amount", [-0.50, 0.0, 15.01])
def test_refund_late_fee_invalid_amounts_neg_zero_high(mocker, amount):
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    success, msg = lib_service.refund_late_fee_payment(f"txn_{patron_id}_", amount, payment_gateway = gateway)

    assert success is False
    assert "Refund amount" in msg
    gateway.refund_payment.assert_not_called()

## -------------------- Additional tests to ensure more than 80% coverage --------------------

# invalid book ID (verify mock NOT called) - pay late fee
def stub_get_book_by_id_not_found(mocker):
    return mocker.patch.object(
        lib_service, 
        "get_book_by_id",
        autospec = True,
        return_value = None
    )

def test_pay_late_fee_invalid_book_id(mocker):
    stub_get_book_by_id_not_found(mocker)
    stub_calc_late_fee(mocker, 3.00) # price for 6 days overdue
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    success, msg, txn = lib_service.pay_late_fees(patron_id, 5, payment_gateway = gateway)

    assert success is False
    assert "Book not found" in msg
    assert txn is None
    gateway.process_payment.assert_not_called()

# invalid fee amount - pay late fee
def stub_calc_late_fee_none(mocker):
    return mocker.patch.object(
        lib_service, 
        "calculate_late_fee_for_book",
        autospec = True,
        return_value = None
    )

def test_pay_late_fee_invalid_fee_amount(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee_none(mocker) # invalid late fee
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    success, msg, txn = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is False
    assert "Unable to calculate late fees" in msg
    assert txn is None
    gateway.process_payment.assert_not_called()

# network error exception handling - refund late fee
def test_refund_late_fee_network_error(mocker):
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.side_effect = Exception("Network Error")
    success, msg = lib_service.refund_late_fee_payment(f"txn_{patron_id}_", 10.0, payment_gateway = gateway)

    assert success is False
    assert "Refund processing error" in msg
    gateway.refund_payment.assert_called_once_with(f"txn_{patron_id}_", 10.0)

# refund declined by gateway - refund late fee
def test_refund_late_fee_gateway_declined(mocker):
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (False, "Invalid refund amount")
    success, msg = lib_service.refund_late_fee_payment(f"txn_{patron_id}_", 10.0, payment_gateway = gateway)

    assert success is False
    assert "Refund failed" in msg
    gateway.refund_payment.assert_called_once_with(f"txn_{patron_id}_", 10.0)

# invalid author - add book to catalog (R1)
def test_add_book_invalid_no_author(mocker):
    #vars
    isbn = "1234567890124"
    total_copies = 5

    # add book to catalog
    success, message = lib_service.add_book_to_catalog("Test Book", None, isbn, total_copies)
    
    assert success == False
    assert "author is required" in message.lower()

# duplicate isbn - add book to catalog (R1)
def stub_get_book_by_isbn(mocker):
    return mocker.patch.object(
        lib_service, 
        "get_book_by_isbn",
        autospec = True,
        return_value = {
            "id": 1
        }
    )

def test_add_book_duplicate_isbn(mocker):
    #vars
    isbn = "1234567890124"
    total_copies = 1
    stub_get_book_by_isbn(mocker)
    # add book to catalog
    success, message = lib_service.add_book_to_catalog("Test Book", "Author", isbn, total_copies)
    
    assert success == False
    assert "already exists" in message.lower()

# database error - add book to catalog (R1)
def stub_get_book_by_isbn_none(mocker):
    return mocker.patch.object(
        lib_service, 
        "get_book_by_isbn",
        autospec = True,
        return_value = None
    )

def stub_insert_book(mocker):
    return mocker.patch.object(
        lib_service, 
        "insert_book",
        autospec = True,
        return_value = False
    )

def test_add_book_database_error(mocker):
     #vars
    isbn = "1234567890124"
    total_copies = 1
    stub_get_book_by_isbn_none(mocker)
    stub_insert_book(mocker)

    # add book to catalog
    success, message = lib_service.add_book_to_catalog("Test Book", "Author", isbn, total_copies)
    
    assert success == False
    assert "database error" in message.lower()

# invalid patron ID - calc late fee
def test_calc_late_fee_invalid_patron(mocker):
    result = lib_service.calculate_late_fee_for_book("ABC123", 1)
    assert result["status"] == "Invalid patron ID"

# book not found - calc late fee
def test_calc_late_fee_book_not_found(mocker):
    stub_get_book_by_id_not_found(mocker)
    result = lib_service.calculate_late_fee_for_book("123456", 1)

    assert result["fee_amount"] == 0.0
    assert result["days_overdue"] == 0
    assert result["status"] == "Book not found."

# invalid search type - search books in catalog
def test_search_invalid_types(mocker):
    assert lib_service.search_books_in_catalog(123, "title") == []

# invalid empty search term - search books in catalog
def test_search_empty_term(mocker):
    assert lib_service.search_books_in_catalog("   ", "title") == []

# invalid patron - return book by patron
def test_return_book_invalid_patron(mocker):
    success, msg = lib_service.return_book_by_patron("ABC", 1)
    assert not success
    assert "Invalid patron ID" in msg
