import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--send_emails", 
        action="store_true", 
        default=False, 
        help="Send actual emails over the network to a test inbox"
    )
