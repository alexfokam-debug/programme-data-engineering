def get_order_summary(order):
    """
    Item 05
    Function to generate a summary of an order.

    The goal is to use tuple unpacking to extract multiple values from one tuple instead of using indexing
    for the lecture of the order tuple. This makes the code more readable and maintainable.
    """
    order_id, customer, amount = order
    return f'Order Summary: Order ID: {order_id}, Customer: {customer}, Amont: {amount}'


def create_single_item_tuple(product):
    """
    Item 06

    Function to create a single-item tuple.
    
    The goal is to demonstrate the correct way to create a single-item tuple in Python. 
    A single-item tuple must have a trailing comma after the item, otherwise it will be interpreted as a regular parenthesis.
    """
    return (product,)





