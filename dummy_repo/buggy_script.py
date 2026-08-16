```python
def divide(a, b):
    try:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return "Error: Both inputs must be numbers"
        if b == 0:
            return "Error: Division by zero"
        return a / b
    except TypeError:
        return "Error: Invalid input type"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
```