import datetime
from decimal import Decimal
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation

def test_memento_to_and_from_dict():
    calc = Calculation.from_dict({
        'operation': 'Addition',
        'operand1': '5',
        'operand2': '3',
        'result': '8',
        'timestamp': datetime.datetime.now().isoformat()
    })
    memento = CalculatorMemento([calc])
    data = memento.to_dict()
    assert 'history' in data
    assert 'timestamp' in data
    assert len(data['history']) == 1

    restored = CalculatorMemento.from_dict(data)
    assert len(restored.history) == 1
    assert restored.history[0].operand1 == Decimal('5')
    assert restored.history[0].operand2 == Decimal('3')
    assert str(restored.history[0].operation) == 'Addition'
