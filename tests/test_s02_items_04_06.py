from python.effective_python.s02_items_04_06 import create_single_item_tuple


def test_create_single_item_tuple():
    """
    Test function for create_single_item_tuple.

    This function tests the create_single_item_tuple function to ensure it correctly creates a single-item tuple.
    It checks the type of the returned value and verifies that it is indeed a tuple with one item.
    """
    single_item = create_single_item_tuple("Laptop")
    assert isinstance(single_item, tuple), "The result should be a tuple."
    assert len(single_item) == 1, "The tuple should contain exactly one item."
    assert single_item[0] == "Laptop", "The item in the tuple should be 'Laptop'."
