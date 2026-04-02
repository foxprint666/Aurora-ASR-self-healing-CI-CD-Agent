import pytest
from src.processor import process_data, normalize_results

def test_process_data_empty():
    # Bug: This currently raises ZeroDivisionError
    assert process_data([]) == 0.0

def test_process_data_valid():
    assert process_data([10, 20, 30]) == 20.0
    assert process_data(["10", 20]) == 15.0

def test_normalize():
    assert normalize_results([20, 10, 0]) == [1.0, 0.5, 0.0]
