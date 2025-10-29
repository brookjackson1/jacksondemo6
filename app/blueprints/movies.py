from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import requests
import os
from dotenv import load_dotenv

load_dotenv()

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/movies')
def index():
    """Display all movies"""
    connection = get_db()
    result = []

    if connection is None:
        flash("Database connection failed. Please check your database configuration.", "error")
    else:
        try:
            query = "SELECT * FROM movies ORDER BY title"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
        except Exception as e:
            flash(f"Database error: {e}", "error")
            result = []

    return render_template("movies.html", movies=result)


@movies_bp.route('/movies/add', methods=['POST'])
def add_movie():
    """Add movie with just the title"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('movies.index'))

    title = request.form.get('title', '').strip()

    if not title:
        flash("Movie title is required.", "error")
        return redirect(url_for('movies.index'))

    try:
        query = """
        INSERT INTO movies (title, director, year, plot, poster, actors, genre)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        # Insert with just title, other fields null
        with connection.cursor() as cursor:
            cursor.execute(query, (title, None, None, None, None, None, None))
        connection.commit()

        flash(f"Movie '{title}' added successfully! Click 'Fetch Data' to get movie details from OMDB.", "success")
    except Exception as e:
        flash(f"Error adding movie: {e}", "error")

    return redirect(url_for('movies.index'))


@movies_bp.route('/movies/fetch/<int:movie_id>')
def fetch_data(movie_id):
    """Fetch data from OMDB API and update"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('movies.index'))

    try:
        # Get the movie title from database
        query = "SELECT title FROM movies WHERE movie_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()

        if not movie:
            flash("Movie not found.", "error")
            return redirect(url_for('movies.index'))

        title = movie['title']

        # Fetch data from OMDB API
        movie_data = fetch_omdb_data(title)

        if movie_data is None:
            api_key = os.getenv('OMDB_API_KEY')
            if not api_key:
                flash(f"OMDB API key is not configured. Please set OMDB_API_KEY in environment variables.", "error")
            else:
                flash(f"Could not fetch data for '{title}' from OMDB API. The movie may not exist in OMDB database.", "error")
            return redirect(url_for('movies.index'))

        # Update database with fetched data
        update_query = """
        UPDATE movies
        SET director = %s, year = %s, plot = %s, poster = %s, actors = %s, genre = %s
        WHERE movie_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(update_query, (
                movie_data.get('director'),
                movie_data.get('year'),
                movie_data.get('plot'),
                movie_data.get('poster'),
                movie_data.get('actors'),
                movie_data.get('genre'),
                movie_id
            ))
        connection.commit()

        flash(f"Movie data fetched and updated for '{title}'!", "success")

    except Exception as e:
        flash(f"Error fetching movie data: {e}", "error")

    return redirect(url_for('movies.index'))


@movies_bp.route('/movies/view/<int:movie_id>')
def view_movie(movie_id):
    """View detailed movie information"""
    connection = get_db()
    movie = None

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('movies.index'))

    try:
        query = "SELECT * FROM movies WHERE movie_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()

        if not movie:
            flash("Movie not found.", "error")
            return redirect(url_for('movies.index'))

    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('movies.index'))

    return render_template("movie_detail.html", movie=movie)


@movies_bp.route('/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    """Edit movie information"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('movies.index'))

    if request.method == 'POST':
        # Handle POST request - update movie
        title = request.form.get('title', '').strip()
        director = request.form.get('director', '').strip()
        year = request.form.get('year', type=int)
        plot = request.form.get('plot', '').strip()
        poster = request.form.get('poster', '').strip()
        actors = request.form.get('actors', '').strip()
        genre = request.form.get('genre', '').strip()

        if not title:
            flash("Movie title is required.", "error")
            return redirect(url_for('movies.edit_movie', movie_id=movie_id))

        try:
            query = """
            UPDATE movies
            SET title = %s, director = %s, year = %s, plot = %s, poster = %s, actors = %s, genre = %s
            WHERE movie_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(query, (title, director, year, plot, poster, actors, genre, movie_id))
            connection.commit()

            flash(f"Movie '{title}' updated successfully!", "success")
            return redirect(url_for('movies.index'))
        except Exception as e:
            flash(f"Error updating movie: {e}", "error")

    # Handle GET request - show edit form
    try:
        query = "SELECT * FROM movies WHERE movie_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()

        if not movie:
            flash("Movie not found.", "error")
            return redirect(url_for('movies.index'))

        return render_template("movie_edit.html", movie=movie)

    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('movies.index'))


@movies_bp.route('/movies/delete/<int:movie_id>')
def delete_movie(movie_id):
    """Delete movie from database"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('movies.index'))

    try:
        # Get movie title for confirmation message
        query = "SELECT title FROM movies WHERE movie_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()

        if not movie:
            flash("Movie not found.", "error")
            return redirect(url_for('movies.index'))

        title = movie['title']

        # Delete the movie
        delete_query = "DELETE FROM movies WHERE movie_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(delete_query, (movie_id,))
        connection.commit()

        flash(f"Movie '{title}' deleted successfully!", "success")

    except Exception as e:
        flash(f"Error deleting movie: {e}", "error")

    return redirect(url_for('movies.index'))


def fetch_omdb_data(title):
    """
    Fetch movie data from OMDB API
    Get a free API key at: http://www.omdbapi.com/apikey.aspx
    """
    api_key = os.getenv('OMDB_API_KEY')

    if not api_key:
        print("Warning: OMDB_API_KEY not set in environment variables")
        return None

    try:
        url = "http://www.omdbapi.com/"
        params = {
            'apikey': api_key,
            't': title,  # Search by title
            'type': 'movie',
            'plot': 'full'  # Get full plot
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check if movie was found
        if data.get('Response') == 'False':
            print(f"[ERROR] Movie not found: {data.get('Error', 'Unknown error')}")
            return None

        # Extract and return movie data
        movie_data = {
            'director': data.get('Director', ''),
            'year': int(data.get('Year', '0').split('–')[0]) if data.get('Year') and data.get('Year') != 'N/A' else None,
            'plot': data.get('Plot', ''),
            'poster': data.get('Poster', '') if data.get('Poster') != 'N/A' else '',
            'actors': data.get('Actors', ''),
            'genre': data.get('Genre', '')
        }

        print(f"[SUCCESS] Fetched data for: {title}")
        return movie_data

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"[ERROR] Error parsing API response: {e}")
        return None
