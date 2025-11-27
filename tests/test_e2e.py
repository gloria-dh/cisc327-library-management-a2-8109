from playwright.sync_api import Page, expect
import random, database
import os
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Skip Playwright E2E tests in CI. No live server running."
)

BASE_URL = "http://localhost:5000" # From student inst.

def test_e2e_add_book_to_catalog_and_borrow_book(page: Page):

    # -------------------- FLOW 1 --------------------
    # Create a random ISBN to avoid duplicates
    session_isbn = str(random.randint(10**12, 10**13 - 1))

    # Go to add_book route
    page.goto(BASE_URL + "/add_book")

    # Fill in the form to add a book
    page.fill("input[name='title']", "E2E Test Book")
    page.fill("input[name='author']", "E2E Test Author")
    page.fill("input[name='isbn']", session_isbn)
    page.fill("input[name='total_copies']", "2")

    # Submit the form
    page.click("text=Add Book to Catalog")

    # Wait for redirect to catalog
    page.wait_for_url(BASE_URL + "/catalog")

    # ASSERT: book appears in catalog table
    row = page.get_by_role("row").filter(has_text=session_isbn)
    expect(row).to_be_visible()
    expect(row.get_by_role("cell", name="E2E Test Book")).to_be_visible()
    expect(row.get_by_role("cell", name="E2E Test Author")).to_be_visible()

    # -------------------- FLOW 2 --------------------
    patron = "111111" # patron ID

    # Fill patron ID in row
    row.locator("input[name='patron_id']").fill(patron)

    # Submit form in same row
    row.get_by_role("button", name="Borrow").click()
    
    # Check confirmation message
    expect(page.get_by_text("Successfully borrowed \"E2E Test Book\"")).to_be_visible()
