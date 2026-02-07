from tools.registry import register_tool

@register_tool("check_balance")
def check_balance(data):
    return {
        "account_number": "12345678",
        "balance": "£1,250.00",
        "currency": "GBP"
    }

@register_tool("validate_customer")
def validate_customer(data):
    return {
        "customer_id": data.get("customer_id"),
        "status": "VALID"
    }
