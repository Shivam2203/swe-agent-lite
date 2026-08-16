```python
def divide(a, b):
    try:
        if a is None or b is None:
            return "Error: Inputs cannot be empty"
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return "Error: Both inputs must be numbers"
        if b == 0:
            return "Error: Division by zero"
        return a / b
    except ZeroDivisionError:
        return "Error: Division by zero"
    except TypeError:
        return "Error: Invalid input type"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
```