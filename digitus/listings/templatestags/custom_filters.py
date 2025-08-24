from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    return f"{Decimal(value) * Decimal(arg):.2f}"

@register.filter
def sum_prices(items):
    return sum(item.listing.price for item in items)

@register.filter
def sum_seller_amounts(orders):
    return sum(order.seller_amount for order in orders)