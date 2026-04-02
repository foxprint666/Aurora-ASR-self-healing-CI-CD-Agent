def process_data(data):
    if not data:
        # Bug: Should return 0.0 or raise specific error instead of division by zero
        return sum(data) / len(data)
    
    # Complex transformation
    total = 0
    for item in data:
        if isinstance(item, (int, float)):
            total += item
        elif isinstance(item, str) and item.isdigit():
            total += int(item)
            
    return total / len(data)

def normalize_results(results):
    max_val = max(results) if results else 1
    return [x / max_val for x in results]
