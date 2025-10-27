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
        
    def patch(self, expense_id):
        data = request.get_json()
        expense = Expense.query.get(expense_id)

        if not expense:
            return {'error': 'Expense not found'}, 404

        if 'expense_name' in data:
            expense.expense_name = data['expense_name']

        if 'amount' in data:
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    return {'error': 'Amount must be positive'}, 400
                expense.amount = amount
            except ValueError:
                return {'error': 'Invalid amount'}, 400

        if 'payment_method' in data:
            if data['payment_method'] not in [pm.value for pm in ExpensePaymentMethod]:
                return {'error': 'Invalid payment method. Must be cash or mpesa'}, 400
            expense.payment_method = ExpensePaymentMethod(data['payment_method'])

        if 'date' in data:
            try:
                expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400

        try:
            db.session.commit()
            return expense.to_dict(), 200
        except Exception:
            db.session.rollback()
            return {'error': 'Failed to update expense'}, 500
        
    def delete(self, expense_id):
        expense = Expense.query.get(expense_id)
        if not expense:
            return {'error': 'Expense not found'}, 404

        try:
            db.session.delete(expense)
            db.session.commit()
            return {'message': 'Expense deleted successfully'}, 200
        except Exception:
            db.session.rollback()
            return {'error': 'Failed to delete expense'}, 500