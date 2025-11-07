from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Enum
from datetime import date
import enum

db = SQLAlchemy()

class PaymentMethod(enum.Enum):
    CASH = "CASH"
    MPESA = "MPESA"
    TILL = "TILL"
    INVOICE = "INVOICE"
    CARD = "CARD"

class ExpensePaymentMethod(enum.Enum):
    CASH = "CASH"
    MPESA = "MPESA"

class Collection(db.Model, SerializerMixin):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    card_no = db.Column(db.String(50), nullable=False)
    procedure = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(Enum(PaymentMethod), nullable=False)
    invoice_source = db.Column(db.String(100), nullable=True)  # Only for invoice payments
    amount = db.Column(db.Float)
    doctor =  db.Column(db.String(100))
    date = db.Column(db.Date, default=date.today, nullable=False)

class Expense(db.Model, SerializerMixin):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    expense_name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(Enum(ExpensePaymentMethod), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)

    @staticmethod
    def get_day_tallies(target_date):
        """Get all collections and expenses for a specific date with computed tallies"""
        collections = Collection.query.filter_by(date=target_date).all()
        expenses = Expense.query.filter_by(date=target_date).all()

        # Compute collection totals by payment method
        cash_total = sum(c.amount for c in collections if c.payment_method == PaymentMethod.CASH)
        mpesa_total = sum(c.amount for c in collections if c.payment_method == PaymentMethod.MPESA)
        till_total = sum(c.amount for c in collections if c.payment_method == PaymentMethod.TILL)
        invoice_total = sum(c.amount for c in collections if c.payment_method == PaymentMethod.INVOICE)
        card_total = sum(c.amount for c in collections if c.payment_method == PaymentMethod.CARD)

        # Mobile money total with till deduction
        mobile_money_total = till_total * 0.9945 + mpesa_total

        # Gross collections
        gross_collections = cash_total + mobile_money_total + invoice_total + card_total

        # Total expenses
        total_expenses = sum(e.amount for e in expenses)

        # Net total
        net_total = gross_collections - total_expenses

        # Cash in hand
        cash_in_hand = (mobile_money_total + cash_total) - total_expenses

        return {
            'date': target_date.isoformat(),
            'collections': [c.to_dict() for c in collections],
            'expenses': [e.to_dict() for e in expenses],
            'totals': {
                'cash_total': cash_total,
                'mpesa_total': mpesa_total,
                'till_total': till_total,
                'invoice_total': invoice_total,
                'card_total': card_total,
                'mobile_money_total': mobile_money_total,
                'gross_collections': gross_collections,
                'total_expenses': total_expenses,
                'net_total': net_total,
                'cash_in_hand': cash_in_hand
            }
        }

    @staticmethod
    def get_month_tallies(month, year):
        """Get monthly summary for all days in the month"""
        from calendar import monthrange
        import datetime

        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        daily_summaries = []
        monthly_totals = {
            'total_gross_collections': 0,
            'total_expenses': 0,
            'total_net': 0,
            'days_count': 0
        }

        current_date = start_date
        while current_date <= end_date:
            day_data = Expense.get_day_tallies(current_date)
            if day_data['collections'] or day_data['expenses']:  # Only include days with data
                daily_summaries.append(day_data)
                monthly_totals['total_gross_collections'] += day_data['totals']['gross_collections']
                monthly_totals['total_expenses'] += day_data['totals']['total_expenses']
                monthly_totals['total_net'] += day_data['totals']['net_total']
                monthly_totals['days_count'] += 1
            current_date += datetime.timedelta(days=1)

        return {
            'month': f"{year}-{month:02d}",
            'daily_summaries': daily_summaries,
            'monthly_totals': monthly_totals
        }