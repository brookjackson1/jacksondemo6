from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd

examples = Blueprint('examples', __name__)

@examples.route('/')
def show_examples():
    connection = get_db()
    
    # Check if we need to load data for modals
    edit_example = None
    delete_example = None
    result = []
    
    edit_id = request.args.get('edit_id')
    delete_id = request.args.get('delete_id')
    
    # Check database connection once
    if connection is None:
        flash("Database connection failed. Please check your database configuration.", "error")
    else:
        try:
            if edit_id:
                query = "SELECT * FROM athletes_data WHERE athlete_id = %s"
                with connection.cursor() as cursor:
                    cursor.execute(query, (edit_id,))
                    edit_example = cursor.fetchone()
            
            if delete_id:
                query = "SELECT * FROM athletes_data WHERE athlete_id = %s"
                with connection.cursor() as cursor:
                    cursor.execute(query, (delete_id,))
                    delete_example = cursor.fetchone()
            
            # Get all examples for the table
            query = "SELECT * FROM athletes_data"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                
        except Exception as e:
            flash(f"Database error: {e}", "error")
            result = []
    
    if result:
        df = pd.DataFrame(result)
        # Add edit and delete buttons to the Actions column
        def create_actions(row):
            id = row['athlete_id']
            return (f'<a href="{url_for("examples.show_examples", edit_id=id)}" class="btn btn-sm btn-info">Edit</a> '
                   f'<a href="{url_for("examples.show_examples", delete_id=id)}" class="btn btn-sm btn-danger">Delete</a>')
        
        df['Actions'] = df.apply(create_actions, axis=1)
        table_html = df.to_html(classes='table table-striped table-bordered', index=False, header=False, escape=False)
        rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]
    else:
        rows_only = ""
    
    return render_template("examples.html", table=rows_only, edit_example=edit_example, delete_example=delete_example)

@examples.route('/edit/<int:athlete_id>', methods=['POST'])
def edit_example(athlete_id):
    connection = get_db()
    
    name = request.form.get('name')
    position = request.form.get('position')
    goals = request.form.get('goals', type=int, default=0)
    assists = request.form.get('assists', type=int, default=0)
    club_name = request.form.get('club_name')
    
    query = """
    UPDATE athletes_data
    SET name = %s, position = %s, goals = %s, assists = %s, club_name = %s
    WHERE athlete_id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (name, position, goals, assists, club_name, athlete_id))
    connection.commit()
    
    flash("Example updated successfully!", "success")
    return redirect(url_for('examples.show_examples'))

@examples.route('/delete/<int:athlete_id>', methods=['POST'])
def delete_example(athlete_id):
    connection = get_db()
    query = "DELETE FROM athletes_data WHERE athlete_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (athlete_id,))
    connection.commit()
    
    flash("Example deleted successfully!", "success")
    return redirect(url_for('examples.show_examples'))

@examples.route('/add', methods=['POST'])
def add_example():
    connection = get_db()
    
    name = request.form.get('name')
    position = request.form.get('position')
    goals = request.form.get('goals', type=int, default=0)
    assists = request.form.get('assists', type=int, default=0)
    points = request.form.get('points', type=int, default=0)
    club_name = request.form.get('club_name')
    
    query = """
    INSERT INTO athletes_data (name, position, goals, assists, points, club_name)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (name, position, goals, assists, points, club_name))
    connection.commit()
    
    flash("New example added successfully!", "success")
    return redirect(url_for('examples.show_examples'))