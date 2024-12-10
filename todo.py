from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Task {self.name}>'

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Add new task
        task_name = request.form['task_name']
        due_date = request.form['due_date']
        priority = request.form['priority']

        # Validate inputs
        if not task_name or not due_date or not priority:
            flash('All fields are required!', 'error')
            return redirect(url_for('index'))

        try:
            new_task = Task(
                name=task_name, 
                due_date=datetime.strptime(due_date, '%Y-%m-%d').date(), 
                priority=priority
            )
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding task: {str(e)}', 'error')
            db.session.rollback()

        return redirect(url_for('index'))

    # Fetch all tasks, sorted by priority and due date
    tasks = Task.query.order_by(
        db.case(./index.html
            (Task.priority == 'High', 1),
            (Task.priority == 'Medium', 2),
            (Task.priority == 'Low', 3)
        ),
        Task.due_date
    ).all()
    
    return render_template('index.html', tasks=tasks)

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        # Update task
        task.name = request.form['task_name']
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        task.priority = request.form['priority']

        try:
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating task: {str(e)}', 'error')
            db.session.rollback()

    return render_template('edit.html', task=task)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting task: {str(e)}', 'error')
        db.session.rollback()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
