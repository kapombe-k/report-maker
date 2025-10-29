from flask_restful import Resource
from flask import request
from models import db, Collection, PaymentMethod
from datetime import datetime

class CollectionResource(Resource):
    def get(self, date=None):
        if date:
            try:
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
                collections = Collection.query.filter_by(date=target_date).all()
                return [c.to_dict() for c in collections], 200
            except ValueError:
                return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400
        else:
            collections = Collection.query.all()
            return [c.to_dict() for c in collections], 200

    def post(self):
        data = request.get_json()

        # Manual validation
        required_fields = ['card_no', 'procedure', 'payment_method', 'amount', 'doctor']
        for field in required_fields:
            if field not in data or not data[field]:
                return {'error': f'{field} is required'}, 400

        if data['payment_method'] not in [pm.value for pm in PaymentMethod]:
            return {'error': 'Invalid payment method'}, 400

        if data['payment_method'] == 'invoice' and 'invoice_source' not in data:
            return {'error': 'invoice_source is required for invoice payments'}, 400

        if 'invoice_source' in data and data['payment_method'] != 'invoice':
            return {'error': 'invoice_source should only be provided for invoice payments'}, 400

        date = data.get('date')
        if date:
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400
        else:
            from datetime import date
            date = date.today()

        amount = float(data['amount'])

        collection = Collection(
            card_no=data['card_no'],
            procedure=data['procedure'],
            payment_method=PaymentMethod(data['payment_method']),
            invoice_source=data.get('invoice_source'),
            doctor = data['doctor'],
            amount=amount,
            date=date
        )

        try:
            db.session.add(collection)
            db.session.commit()
            return collection.to_dict(), 201
        except Exception:
            db.session.rollback()
            return {'error': 'Failed to save collection'}, 500
        
    def patch(self, collection_id):
        collection = Collection.query.get(collection_id)
        if not collection:
            return {'error': 'Collection not found'}, 404

        data = request.get_json()

        if 'card_no' in data:
            collection.card_no = data['card_no']
        if 'procedure' in data:
            collection.procedure = data['procedure']
        if 'payment_method' in data:
            if data['payment_method'] not in [pm.value for pm in PaymentMethod]:
                return {'error': 'Invalid payment method'}, 400
            payment_method = PaymentMethod(data['payment_method'])
            collection.payment_method = PaymentMethod(data['payment_method'])
        if 'invoice_source' in data:
            collection.invoice_source = data['invoice_source']
        if 'amount' in data:
            collection.amount = float(data['amount'])
        if 'doctor' in data:
            collection.doctor = data['doctor']
        if 'date' in data:
            try:
                collection.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400

        try:
            db.session.commit()
            return collection.to_dict(), 200
        except Exception:
            db.session.rollback()
            return {'error': 'Failed to update collection'}, 500
        
    def delete(self, collection_id):
        collection = Collection.query.get(collection_id)
        if not collection:
            return {'error': 'Collection not found'}, 404

        try:
            db.session.delete(collection)
            db.session.commit()
            return {'message': 'Collection deleted successfully'}, 200
        except Exception:
            db.session.rollback()
            return {'error': 'Failed to delete collection'}, 500
                        
