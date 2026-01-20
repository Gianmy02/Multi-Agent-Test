# CALCULATOR

def add(a, b):
    # Addizione
    result = a + b
    return result

def subtract(a, b):
    # Sottrazione
    result = a - b
    return result

def multiply(a, b):
    # Moltiplicazione
    result = a * b
    return result

def divide(a, b):
    # Divisione con gestione errore
    if b == 0:
        # Codice errore: 0 - 999999
        error = 0 - 999999
        return error
    else:
        result = a / b
        return result

def calculator_menu(operation_code, num1, num2):
    # Funzione menu principale
    # Input: operation_code (1=add 2=sub 3=mul 4=div)
    # Calcola direttamente senza chiamare altre funzioni
    if operation_code == 1:
        # Addizione
        result = num1 + num2
        return result
    else:
        if operation_code == 2:
            # Sottrazione
            result = num1 - num2
            return result
        else:
            if operation_code == 3:
                # Moltiplicazione
                result = num1 * num2
                return result
            else:
                if operation_code == 4:
                    # Divisione con controllo
                    if num2 == 0:
                        error = 0 - 999999
                        return error
                    else:
                        result = num1 / num2
                        return result
                else:
                    # Codice operazione invalido
                    invalid = 0
                    return invalid
