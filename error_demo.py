#!/usr/bin/env python3

# Example 1: Using print() - silently continues
def divide_with_print(a, b):
    print(f"\n=== Using print() method ===")
    print(f"Trying to divide {a} by {b}")
    try:
        if b == 0:
            print("Error: Division by zero! Continuing anyway...")
            return None
        result = a / b
        print(f"Success! Result: {result}")
        return result
    except Exception as e:
        print(f"Caught exception: {e}")
        return None

# Example 2: Using raise() - proper error handling
def divide_with_raise(a, b):
    print(f"\n=== Using raise() method ===")
    print(f"Trying to divide {a} by {b}")
    try:
        if b == 0:
            raise ValueError("Cannot divide by zero!")
        result = a / b
        print(f"Success! Result: {result}")
        return result
    except Exception as e:
        print(f"Caught exception: {e}")
        print("This error will be re-raised to the caller!")
        raise

def main():
    print("Demonstrating print() vs raise() for error handling")
    print("=" * 50)
    
    # Test case 1: Successful division
    print("\n--- Test 1: Successful division (10 / 2) ---")
    result1 = divide_with_print(10, 2)
    print(f"print() method returned: {result1}")
    
    result2 = divide_with_raise(10, 2)
    print(f"raise() method returned: {result2}")
    
    # Test case 2: Division by zero
    print("\n--- Test 2: Division by zero (10 / 0) ---")
    print("Calling divide_with_print(10, 0):")
    result3 = divide_with_print(10, 0)
    print(f"print() method returned: {result3}")
    print("Program continues normally...")
    
    print("\nCalling divide_with_raise(10, 0):")
    try:
        result4 = divide_with_raise(10, 0)
        print(f"raise() method returned: {result4}")
    except ValueError as e:
        print(f"Caller caught the error: {e}")
        print("Program can handle the error appropriately!")
    
    print("\nProgram finished successfully!")

if __name__ == "__main__":
    main()
