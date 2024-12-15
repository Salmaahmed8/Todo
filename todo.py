from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# File to store tasks
TASKS_FILE = 'tasks.json'

# Ensure tasks file exists
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, 'w') as file:
        json.dump([], file)


# Helper functions to interact with the JSON "database"
def load_tasks():
    with open(TASKS_FILE, 'r') as file:
        return json.load(file)


def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)


# Route: Display tasks and handle task creation
@app.route('/', methods=['GET', 'POST'])
def index():
    tasks = load_tasks()

    if request.method == 'POST':
        # Collect form data
        task_name = request.form['task_name']
        due_date = request.form['due_date']
        priority = request.form['priority']

        # Validate inputs
        if not task_name or not due_date or not priority:
            flash('All fields are required!', 'error')
            return redirect(url_for('index'))

        try:
            new_task = {
                "id": max([task["id"] for task in tasks], default=0) + 1,
                "name": task_name,
                "due_date": due_date,
                "priority": priority
            }
            tasks.append(new_task)
            save_tasks(tasks)
            flash('Task added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding task: {str(e)}', 'error')

        return redirect(url_for('index'))

    # Sort tasks: Priority (High -> Medium -> Low) then due_date
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    tasks.sort(key=lambda t: (priority_order.get(t["priority"], 4), t["due_date"]))

    return render_template('index.html', tasks=tasks)


# Route: Edit a task
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)

    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        task['name'] = request.form['task_name']
        task['due_date'] = request.form['due_date']
        task['priority'] = request.form['priority']

        try:
            save_tasks(tasks)
            flash('Task updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating task: {str(e)}', 'error')

    return render_template('edit.html', task=task)


# Route: Delete a task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]

    try:
        save_tasks(tasks)
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting task: {str(e)}', 'error')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
