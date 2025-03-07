# scripts/test_suite.py
from test_mint import test_mint
from test_novena import test_start_novena
from test_complete_novena import test_complete_novena
from test_batch_complete import test_batch_complete
from test_transfer import test_transfer
from test_status import test_status
from test_withdraw import test_withdraw

def run_test_suite():
    print("Running Test Suite...")
    test_mint()
    test_start_novena(stag_id=2)
    test_transfer(stag_id=1, to_address="0xYourTestAddress")  # Replace with real address
    test_complete_novena(stag_id=1)
    test_batch_complete(stag_ids=[1, 2], successful_days=[9, 7])
    test_status()
    test_withdraw()
    print("Test Suite Complete")

if __name__ == "__main__":
    run_test_suite()