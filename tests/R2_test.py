import database


#---------------------------------------------------------------------------------------------------------
# New examples - PASS pytest
#---------------------------------------------------------------------------------------------------------

def test_catalog_renders_valid(client):
    """Renders the catalog page successfully."""
    test = client.get("/catalog")
    assert test.status_code == 200 # succesful rendering status code

def test_catalog_valid(client):
    """Add book to catalog and check if the labels match"""

    # vars
    isbn = "5000000000000"
    total_copies = 1
    avail_copies = 1
    patron_id = "500000"

    # insert book to borrow
    assert database.insert_book("Test Book R2", "Test Author", isbn, total_copies, avail_copies)

    test = client.get("/catalog")
    html_res = test.get_data(as_text = True)
    assert "Test Book R2" in html_res
    assert "Test Author" in html_res
    assert isbn in html_res

def test_catalog_valid_avail_over_total_copies_2_3(client):
    """Add book to catalog and check if the labels match"""

    # vars
    isbn = "0500000000000"
    total_copies = 3
    avail_copies = 2
    patron_id = "050000"

    # insert book to borrow
    assert database.insert_book("Test Book R2", "Test Author", isbn, total_copies, avail_copies)

    test = client.get("/catalog")
    html_res = test.get_data(as_text = True)
    assert "2/3 Available" in html_res

def test_catalog_valid_avail_over_total_copies_0_2(client):
    
    # vars
    isbn = "0050000000000"
    total_copies = 3
    avail_copies = 0
    patron_id = "005000"

    # insert book to borrow
    assert database.insert_book("Test Book R2", "Test Author", isbn, total_copies, avail_copies)

    test = client.get("/catalog")
    html_res = test.get_data(as_text = True)
    assert "0/3 Available" in html_res



