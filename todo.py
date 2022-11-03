from flask import Blueprint, render_template, redirect, g, url_for, flash, request, session
from werkzeug.exceptions import abort

from todo.db import get_db 
from todo.auth import login_required

bp = Blueprint('todo', __name__)

@bp.route('/')
@login_required
def index():
	db, c = get_db()
	c.execute("""select t.created_by, t.crated_at, t.id, t.completed,t.description, u.user
		from todo t JOIN user u on t.created_by = u.id where t.created_by = %s
		order by crated_at desc""",
		(g.user['id'],)
		)
	todos = c.fetchall()

	return render_template('todo/index.html', todos = todos)

@bp.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
	if request.method == 'POST':
		description = request.form['description']
		error = None

		if description is None:
			error = "Se requiere una descripcion"

		if error is not None:
			flash(error)

		else:
			db, c = get_db()
			c.execute('insert into todo(description, completed, created_by) values(%s,%s,%s)', 
				(description, False, g.user['id']) 
				)
			db.commit()
			return redirect(url_for('todo.index'))

		
			
	return render_template('todo/create.html')

def get_todo(id):
	db, c = get_db()
	c.execute(
		"""select t.id, t.description, t.completed, t.crated_at, t.created_by, u.user from todo t JOIN
		 user u on t.created_by = u.id where t.id = %s""",
		(id,)
		)
	todo = c.fetchone()

	if todo is None:
		abort(404, 'El todo de id {} no existe'.format(id))

	return todo

@bp.route('/<int:id>/update', methods = ['GET', 'POST'])
@login_required
def update(id):
	todo = get_todo(id)

	if request.method == "POST":
		description = request.form['description']
		completed = True if request.form.get('completed') == 'on' else False
		error = None

		if description is None:
			error("Se requiere una descripcion")

		if error is not None:
			flash(error)
		else:
			db, c = get_db()
			c.execute(
				"update todo set description = %s, completed = %s where id = %s and created_by = %s",
				(description, completed, id, g.user['id'])
				)
			db.commit()

		return redirect(url_for('todo.index'))

	return render_template('todo/update.html', todo = todo)


@bp.route('/<int:id>/delete', methods = ['POST'])
@login_required
def delete(id):
	db, c = get_db()
	c.execute(
		"delete from todo where id = %s and created_by = %s", (id, g.user['id'])
	)
	db.commit()
	
	return redirect(url_for('todo.index'))
