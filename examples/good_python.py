"""
An example of well-written Python code that should score well.
This demonstrates what BurnBook considers "good" code.
"""

from typing import Optional, List
from dataclasses import dataclass
from enum import Enum


class OrderStatus(Enum):
    """Represents the status of an order."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    """Represents a customer order."""
    id: int
    customer_name: str
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING

    def is_active(self) -> bool:
        """Check if the order is still active."""
        return self.status in (OrderStatus.PENDING, OrderStatus.PROCESSING)


def calculate_total(items: List[dict], tax_rate: float = 0.08) -> float:
    """
    Calculate the total price including tax.
    
    Args:
        items: List of items with 'price' and 'quantity' keys
        tax_rate: Sales tax rate (default 8%)
    
    Returns:
        Total amount including tax
    
    Raises:
        ValueError: If tax_rate is negative
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")
    
    subtotal = sum(item.get("price", 0) * item.get("quantity", 0) for item in items)
    tax = subtotal * tax_rate
    
    return round(subtotal + tax, 2)


def process_order(order: Order, payment_method: Optional[str] = None) -> Order:
    """
    Process an order with the given payment method.
    
    Args:
        order: The order to process
        payment_method: Optional payment method to use
    
    Returns:
        The updated order
    """
    if not order.is_active():
        return order
    
    order.status = OrderStatus.PROCESSING
    
    if payment_method:
        # Process payment logic would go here
        pass
    
    order.status = OrderStatus.COMPLETED
    return order


if __name__ == "__main__":
    # Example usage
    items = [
        {"price": 10.00, "quantity": 2},
        {"price": 25.00, "quantity": 1},
    ]
    
    total = calculate_total(items)
    print(f"Total: ${total}")
    
    order = Order(id=1, customer_name="Alice", total_amount=total)
    process_order(order)
