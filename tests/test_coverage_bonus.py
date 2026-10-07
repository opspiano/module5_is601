import pytest
from unittest.mock import patch
from decimal import Decimal
import datetime
import pathlib
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

def test_calculator_init_load_history_exception():
    with patch.object(Calculator, 'load_history', side_effect=Exception("load failed")):
        calc = Calculator()
        assert calc is not None

def test_calculator_setup_logging_exception():
    calc = Calculator()
    with patch('logging.basicConfig', side_effect=Exception("logging failed")):
        with pytest.raises(Exception):
            calc._setup_logging()

def test_calculator_perform_operation_history_limit():
    calc = Calculator()
    calc.config.max_history_size = 1
    calc.set_operation(OperationFactory.create_operation('add'))
    calc.perform_operation('1', '1')
    calc.perform_operation('2', '2')
    assert len(calc.history) == 1

def test_calculator_perform_operation_unexpected_exception():
    calc = Calculator()
    calc.set_operation(OperationFactory.create_operation('add'))
    with patch('app.calculator.Calculation', side_effect=RuntimeError("unexpected crash")):
        with pytest.raises(OperationError):
            calc.perform_operation('1', '1')

def test_calculator_save_history_exception():
    calc = Calculator()
    with patch('pandas.DataFrame.to_csv', side_effect=Exception("save csv crash")):
        with pytest.raises(OperationError):
            calc.save_history()

def test_calculator_load_history_exception():
    calc = Calculator()
    with patch.object(pathlib.Path, 'exists', return_value=True), \
         patch('pandas.read_csv', side_effect=Exception("read csv crash")):
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
