import pytest
from services.payment_service import PaymentGateway
from services import library_service as lib_service
from unittest.mock import Mock

# -------------------- STUBS --------------------
def stub_get_book_by_id(mocker, book_id = 1, title = "A Tale of Two Cities"):
    return mocker.patch.object(
        lib_service, "get_book_by_id",
        autospec = True,
        return_value = {"id": book_id, "title": title, "author": "Author"}
    )

def stub_calc_late_fee(mocker, amount: float, days_overdue = 6, status = None):
    return mocker.patch.object(
        lib_service, "calculate_late_fee_for_book",
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
    success, msg = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is True
    assert f"txn_{patron_id}_" in msg
    gateway.process_payment.assert_called_once_with(patron_id, 3.0, "Late fees")

# payment declined by gateway
def test_pay_late_fee_gateway_declined(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee(mocker, 1001.0) # gateway is expected to decline this amount
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (False, "", "Payment declined")
    success, msg = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is False
    assert "Payment failed" in msg
    gateway.process_payment.assert_called_once_with(patron_id, 1001.0, "Late fees")

# invalid patron ID (verify mock NOT called)
def test_pay_late_fee_invalid_patron_id(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee(mocker, 3.00) # price for 6 days overdue
    patron_id = "ABC777"

    gateway = Mock(spec=PaymentGateway)
    success, msg = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is False
    assert "Invalid patron ID" in msg
    gateway.process_payment.assert_not_called()

# zero late fees (verify mock NOT called)
def test_pay_late_fee_zero_fee(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee(mocker, 0.0) # no fee
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    success, msg = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is False
    assert "No fee due" in msg
    gateway.process_payment.assert_not_called()

# network error exception handling
def test_pay_late_fee_network_error(mocker):
    stub_get_book_by_id(mocker)
    stub_calc_late_fee(mocker, 3.00) # price for 6 days overdue
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.side_effect = Exception("Network Error")
    success, msg = lib_service.pay_late_fees(patron_id, 1, payment_gateway = gateway)

    assert success is False
    assert "Error processing payment" in msg
    gateway.process_payment.assert_called_once_with(patron_id, 3.00, "Late fees")

## -------------------- refund_late_fee_payment() TESTS --------------------

# succesful refund
def test_refund_late_fee_valid(mocker):
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "processed successfully")
    success, msg = lib_service.refund_late_fee_payment(f"txn_{patron_id}_123", 10.5, payment_gateway = gateway)

    assert success is True
    assert "Refund successful" in msg
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
    assert "Invalid refund amount" in msg
    gateway.refund_payment.assert_not_called()

## -------------------- Additional tests to ensure more than 80% coverage --------------------

# invalid book ID (verify mock NOT called) - pay late fee

def stub_get_book_by_id_not_found(mocker):
    return mocker.patch.object(
        lib_service, "get_book_by_id",
        autospec = True,
        return_value = None
    )

def test_pay_late_fee_invalid_book_id(mocker):
    stub_get_book_by_id_not_found(mocker)
    stub_calc_late_fee(mocker, 3.00) # price for 6 days overdue
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    success, msg = lib_service.pay_late_fees(patron_id, 5, payment_gateway = gateway)

    assert success is False
    assert "Book not found" in msg
    gateway.process_payment.assert_not_called()

# network error exception handling - refund late fee
def test_refund_late_fee_network_error(mocker):
    patron_id = "777777"

    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.side_effect = Exception("Network Error")
    success, msg = lib_service.refund_late_fee_payment(f"txn_{patron_id}_", 10.0, payment_gateway = gateway)

    assert success is False
    assert "Error processing refund" in msg
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

