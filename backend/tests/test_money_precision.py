from sqlalchemy import Numeric

from app.models.balance import Balance
from app.models.betting_plan import BettingPlan
from app.models.platform_ledger import PlatformLedgerEntry
from app.models.settlement import Settlement
from app.models.transaction import Transaction


def test_money_columns_use_two_decimal_fixed_point_storage():
    columns = [
        Balance.__table__.c.available_balance,
        Balance.__table__.c.frozen_balance,
        BettingPlan.__table__.c.bet_amount,
        Transaction.__table__.c.amount,
        Settlement.__table__.c.creator_amount,
        Settlement.__table__.c.participant_amount,
        Settlement.__table__.c.platform_fee,
        Settlement.__table__.c.arbitration_fee,
        PlatformLedgerEntry.__table__.c.amount,
    ]
    assert all(isinstance(column.type, Numeric) for column in columns)
    assert all(column.type.precision == 12 for column in columns)
    assert all(column.type.scale == 2 for column in columns)
    assert all(column.type.asdecimal is False for column in columns)
