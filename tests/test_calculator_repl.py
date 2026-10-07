import pytest
from unittest.mock import patch
from app.calculator_repl import calculator_repl
from app.calculator import Calculator
from decimal import Decimal

def test_repl_help_and_exit(monkeypatch, capsys):
    inputs = iter(['help', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Available commands:" in captured
    assert "Goodbye!" in captured

def test_repl_history_empty_and_populated(monkeypatch, capsys):
    inputs = iter(['clear', 'history', 'add', '2', '3', 'history', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    calculator_repl()
    captured = capsys.readouterr().out
    assert "No calculations in history" in captured
    assert "Result: 5" in captured
    assert "Calculation History:" in captured

def test_repl_clear(monkeypatch, capsys):
    inputs = iter(['add', '2', '3', 'clear', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    calculator_repl()
    captured = capsys.readouterr().out
    assert "History cleared" in captured

def test_repl_undo_redo(monkeypatch, capsys):
    inputs = iter(['undo', 'redo', 'add', '2', '3', 'undo', 'redo', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Nothing to undo" in captured
    assert "Nothing to redo" in captured
    assert "Operation undone" in captured
    assert "Operation redone" in captured

def test_repl_save_load_success(monkeypatch, capsys):
    inputs = iter(['save', 'load', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    calculator_repl()
    captured = capsys.readouterr().out
    assert "History saved successfully" in captured
    assert "History loaded successfully" in captured

def test_repl_save_load_errors(monkeypatch, capsys):
    inputs = iter(['save', 'load', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with patch.object(Calculator, 'save_history', side_effect=Exception("save error")), \
         patch.object(Calculator, 'load_history', side_effect=Exception("load error")):
        calculator_repl()
    captured = capsys.readouterr().out
    assert "Error saving history: save error" in captured
    assert "Error loading history: load error" in captured

def test_repl_cancel_operations(monkeypatch, capsys):
    inputs = iter(['add', 'cancel', 'multiply', '5', 'cancel', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Operation cancelled" in captured

def test_repl_validation_and_operation_error(monkeypatch, capsys):
    inputs = iter(['divide', '5', '0', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Error:" in captured

def test_repl_unexpected_calculation_error(monkeypatch, capsys):
    inputs = iter(['add', '2', '3', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with patch.object(Calculator, 'perform_operation', side_effect=RuntimeError("unexpected calc failure")):
        calculator_repl()
    captured = capsys.readouterr().out
    assert "Unexpected error: unexpected calc failure" in captured

def test_repl_unknown_command(monkeypatch, capsys):
    inputs = iter(['invalid_cmd', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Unknown command: 'invalid_cmd'" in captured

def test_repl_keyboard_interrupt(monkeypatch, capsys):
    calls = 0
    def mock_input(_):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise KeyboardInterrupt
        return 'exit'
    monkeypatch.setattr('builtins.input', mock_input)
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Operation cancelled" in captured

def test_repl_eof_error(monkeypatch, capsys):
    def mock_input(_):
        raise EOFError
    monkeypatch.setattr('builtins.input', mock_input)
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Input terminated. Exiting..." in captured

def test_repl_loop_generic_exception(monkeypatch, capsys):
    calls = 0
    def mock_input(_):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("loop crash")
        return 'exit'
    monkeypatch.setattr('builtins.input', mock_input)
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Error: loop crash" in captured

def test_repl_exit_save_history_warning(monkeypatch, capsys):
    inputs = iter(['exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with patch.object(Calculator, 'save_history', side_effect=Exception("exit save err")):
        calculator_repl()
    captured = capsys.readouterr().out
    assert "Warning: Could not save history: exit save err" in captured

def test_repl_fatal_initialization_error():
    with patch('app.calculator_repl.Calculator', side_effect=Exception("fatal boot")):
        with pytest.raises(Exception, match="fatal boot"):
            calculator_repl()

@pytest.mark.parametrize("op_cmd, op1, op2, expected_res", [
    ('subtract', '10', '4', '6'),
    ('multiply', '3', '7', '21'),
    ('power', '2', '3', '8'),
    ('root', '9', '2', '3'),
])
def test_repl_various_operations(monkeypatch, capsys, op_cmd, op1, op2, expected_res):
    inputs = iter([op_cmd, op1, op2, 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    calculator_repl()
    captured = capsys.readouterr().out
    assert f"Result: {expected_res}" in captured
