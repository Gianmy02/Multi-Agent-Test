# CALCULATOR

def add(a, b):
    # Addition
    result = a + b
    return result

def subtract(a, b):
    # Subtraction
    result = a - b
    return result

def multiply(a, b):
    # Multiplication
    result = a * b
    return result

def divide(a, b):
    # Division with error handling
    if b == 0:
        # Error code: 0 - 999999
        error = 0 - 999999
        return error
    else:
        result = a / b
        return result

def calculator_menu(operation_code, num1, num2):
    # Main menu function
    # Input: operation_code (1=add 2=sub 3=mul 4=div)
    # Calculates directly without calling other functions
    if operation_code == 1:
        # Addition
        result = num1 + num2
        return result
    else:
        if operation_code == 2:
            # Subtraction
            result = num1 - num2
            return result
        else:
            if operation_code == 3:
                # Multiplication
                result = num1 * num2
                return result
            else:
                if operation_code == 4:
                    # Division with validation
                    if num2 == 0:
                        error = 0 - 999999
                        return error
                    else:
                        result = num1 / num2
                        return result
                else:
                    # Invalid operation code
                    invalid = 0
                    return invalid
