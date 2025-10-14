from flask_restful import Resource
from flask import request
from models import db, Expense, ExpensePaymentMethod
from datetime import datetime

class ExpenseResource(Resource):
    def get(self, date=None):
        if date:
            try:
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
                expenses = Expense.query.filter_by(date=target_date).all()
                return [e.to_dict() for e in expenses], 200
            except ValueError:
                return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400
        else:
            expenses = Expense.query.all()
            return [e.to_dict() for e in expenses], 200

    def post(self):
        data = request.get_json()

        # Manual validation
        required_fields = ['expense_name', 'amount', 'payment_method']
        for field in required_fields:
            if field not in data or not data[field]:
                return {'error': f'{field} is required'}, 400

        if data['payment_method'] not in [pm.value for pm in ExpensePaymentMethod]:
            return {'error': 'Invalid payment method. Must be cash or mpesa'}, 400

        try:
            amount = float(data['amount'])
            if amount <= 0:
                return {'error': 'Amount must be positive'}, 400
        except ValueError:
            return {'error': 'Invalid amount'}, 400

        date = data.get('date')
        if date:
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400
        else:
            from datetime import date
            date = date.today()

        expense = Expense(
            expense_name=data['expense_name'],
            amount=amount,
            payment_method=ExpensePaymentMethod(data['payment_method']),
            date=date
        )

        try:
            db.session.add(expense)
            db.session.commit()
            return expense.to_dict(), 201
        except Exception:
            db.session.rollback()
            return {'error': 'Failed to save expense'}, 500