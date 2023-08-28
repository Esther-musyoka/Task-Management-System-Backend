from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import*

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'  # Update with your DB URI
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=False)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    task_list = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'due_date': task.due_date.strftime('%Y-%m-%d')
    } for task in tasks]
    return jsonify(task_list)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if 'title' not in data or 'description' not in data or 'due_date' not in data:
        return jsonify({'error': 'Required fields are missing'}), 400
    try:
        new_task = Task(
            title=data['title'],
            description=data['description'],
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d')
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task created successfully'}), 201
    except (ValueError, IntegrityError):
        db.session.rollback()
        return jsonify({'error': 'Invalid data provided'}), 400

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    try:
        task = Task.query.filter_by(id=task_id).one()
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'due_date' in data:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        db.session.commit()
        return jsonify({'message': 'Task updated successfully'})
    except NoResultFound:
        return jsonify({'error': 'Task not found'}), 404
    except (ValueError, IntegrityError):
        db.session.rollback()
        return jsonify({'error': 'Invalid data provided'}), 400

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id).one()
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': f'Task with id {task_id} deleted successfully'})
    except NoResultFound:
        return jsonify({'error': 'Task not found'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()