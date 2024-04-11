from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import asc

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = []
        for message in Message.query.order_by(asc('created_at')).all(): 
            message_dict = message.to_dict()
            messages.append(message_dict)

        response = make_response(
            messages,
            200
        )

        return response


    elif request.method == 'POST':
        data = request.get_json()
        new_message = Message(
            body=data["body"],
            username=data["username"]
        )

        db.session.add(new_message)
        db.session.commit()
        
        message_dict = new_message.to_dict()

        response = make_response(
            message_dict,
            201
        )

        return response



        

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if not message:
        return jsonify({'error': 'Message not found'}), 404

    if request.method == 'PATCH':
        new_body = request.json.get('body')

        if not new_body:
            return jsonify({'error': 'Body parameter is required for updating'}), 400

        message.body = new_body
        db.session.commit()

        return jsonify(message.to_dict()), 200

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return jsonify({'message': f'Message with id {id} deleted successfully'}), 200
    

if __name__ == '__main__':
    app.run(port=5555)
