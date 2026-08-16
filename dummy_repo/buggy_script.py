```python
def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 'Error: Division by zero'

def greet(name):
    if not name:
        return 'Error: Empty name'
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(divide(10, 2))
    print(divide(10, 0))
    print(greet('John'))
    print(greet(''))
```