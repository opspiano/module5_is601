import pytest
from decimal import Decimal
import datetime
import logging
from app.calculator import Calculator
from app.calculation import Calculation
from app.operations import OperationFactory
from app.exceptions import OperationError

def test_calculation_special_methods():
    calc = Calculation.from_dict({
        'operation': 'Addition',
        'operand1': '5',
        'operand2': '3',
        'result': '8',
        'timestamp': datetime.datetime.now().isoformat()
    })
    assert "Addition(5, 3) = 8" in str(calc)
    assert "Calculation(operation='Addition'" in repr(calc)
    assert calc.__eq__("other") is NotImplemented

def test_calculator_init_load_history_exception(monkeypatch):
    def mock_load(self):
        raise RuntimeError("load failed")
    monkeypatch.setattr(Calculator, 'load_history', mock_load)
    calc = Calculator()
    assert calc is not None

def test_calculator_setup_logging_exception(monkeypatch):
    calc = Calculator()
    def mock_logging(*args, **kwargs):
        raise RuntimeError("logging failed")
    monkeypatch.setattr(logging, 'basicConfig', mock_logging)
    with pytest.raises(Exception):
        calc._setup_logging()

def test_calculator_perform_operation_history_limit():
    calc = Calculator()
    calc.config.max_history_size = 1
    calc.set_operation(OperationFactory.create_operation('add'))
    calc.perform_operation('1', '1')
    calc.perform_operation('2', '2')
    assert len(calc.history) == 1

def test_calculator_perform_operation_unexpected_exception(monkeypatch):
    calc = Calculator()
    calc.set_operation(OperationFactory.create_operation('add'))
    def mock_calc_init(*args, **kwargs):
        raise RuntimeError("unexpected crash")
    monkeypatch.setattr('app.calculator.Calculation', mock_calc_init)
    with pytest.raises(OperationError):
        calc.perform_operation('1', '1')

def test_calculator_save_history_exception(tmp_path):
    class InvalidSaveConfig:
        history_file = tmp_path / "non_existing_dir" / "history.csv"
    calc = Calculator()
    calc.config = InvalidSaveConfig()
    with pytest.raises(OperationError):
        calc.save_history()

def test_calculator_load_history_exception(tmp_path):
    bad_file = tmp_path / "corrupt_history.csv"
    bad_file.write_text("invalid_column1,invalid_column2\n1,2\n")
    class CorruptConfig:
        history_file = bad_file
    calc = Calculator()
    calc.config = CorruptConfig()
    with pytest.raises(OperationError):
        calc.load_history()

def test_calculator_get_history_dataframe_and_show():
    calc = Calculator()
    calc.set_operation(OperationFactory.create_operation('add'))
    calc.perform_operation('10', '20')
    df = calc.get_history_dataframe()
    assert len(df) == 1
    assert df.iloc[0]['operation'] == 'Addition'

    entries = calc.show_history()
    assert len(entries) == 1
    assert "Addition" in entries[0]
    assert "=" in entries[0]

def test_calculator_undo_redo_empty_stacks():
    calc = Calculator()
    calc.undo_stack.clear()
    calc.redo_stack.clear()
    assert calc.undo() is False
    assert calc.redo() is False
