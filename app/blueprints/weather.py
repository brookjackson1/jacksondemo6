from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import requests

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/weather')
def index():
    """Display all weather records"""
    connection = get_db()
    result = []
    edit_weather = None
    delete_weather = None

    edit_id = request.args.get('edit_id')
    delete_id = request.args.get('delete_id')

    if connection is None:
        flash("Database connection failed. Please check your database configuration.", "error")
    else:
        try:
            if edit_id:
                query = "SELECT * FROM weather WHERE weather_id = %s"
                with connection.cursor() as cursor:
                    cursor.execute(query, (edit_id,))
                    edit_weather = cursor.fetchone()

            if delete_id:
                query = "SELECT * FROM weather WHERE weather_id = %s"
                with connection.cursor() as cursor:
                    cursor.execute(query, (delete_id,))
                    delete_weather = cursor.fetchone()

            query = "SELECT * FROM weather ORDER BY city"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
        except Exception as e:
            flash(f"Database error: {e}", "error")
            result = []

    return render_template("weather.html", weather_records=result, edit_weather=edit_weather, delete_weather=delete_weather)


@weather_bp.route('/weather/add', methods=['POST'])
def add_weather():
    """Add new city to database"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('weather.index'))

    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    temperature = request.form.get('temperature', type=float, default=75.0)

    if not city:
        flash("City name is required.", "error")
        return redirect(url_for('weather.index'))

    try:
        query = """
        INSERT INTO weather (city, state, temperature)
        VALUES (%s, %s, %s)
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (city, state, temperature))
        connection.commit()

        flash(f"Weather for {city} added successfully! Click 'Update Weather' to fetch live data.", "success")
    except Exception as e:
        flash(f"Error adding weather: {e}", "error")

    return redirect(url_for('weather.index'))


@weather_bp.route('/weather/update/<int:weather_id>')
def update_weather(weather_id):
    """Fetch live weather from API and update database"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('weather.index'))

    try:
        # First, get the city from database
        query = "SELECT city, state FROM weather WHERE weather_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (weather_id,))
            weather = cursor.fetchone()

        if not weather:
            flash("Weather record not found.", "error")
            return redirect(url_for('weather.index'))

        city = weather['city']
        state = weather['state']

        # Fetch live weather from API
        live_temp = fetch_live_weather(city, state)

        if live_temp is None:
            flash(f"Could not fetch live weather for {city}.", "error")
            return redirect(url_for('weather.index'))

        # Update database with new temperature
        update_query = """
        UPDATE weather
        SET temperature = %s
        WHERE weather_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(update_query, (live_temp, weather_id))
        connection.commit()

        flash(f"Weather updated for {city}: {live_temp:.1f}°F", "success")

    except Exception as e:
        flash(f"Error updating weather: {e}", "error")

    return redirect(url_for('weather.index'))


@weather_bp.route('/weather/edit/<int:weather_id>', methods=['POST'])
def edit_weather(weather_id):
    """Edit existing weather record"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('weather.index'))

    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    temperature = request.form.get('temperature', type=float, default=0.0)

    if not city:
        flash("City name is required.", "error")
        return redirect(url_for('weather.index'))

    try:
        query = """
        UPDATE weather
        SET city = %s, state = %s, temperature = %s
        WHERE weather_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (city, state, temperature, weather_id))
        connection.commit()

        flash(f"Weather for {city} updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating weather: {e}", "error")

    return redirect(url_for('weather.index'))


@weather_bp.route('/weather/delete/<int:weather_id>', methods=['POST'])
def delete_weather(weather_id):
    """Delete weather record"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('weather.index'))

    try:
        query = "DELETE FROM weather WHERE weather_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (weather_id,))
        connection.commit()

        flash("Weather record deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting weather: {e}", "error")

    return redirect(url_for('weather.index'))


def fetch_live_weather(city, state=None):
    """
    Fetch live weather from National Weather Service API (weather.gov)
    This is free and requires no API key!

    Steps:
    1. Get coordinates using OpenStreetMap Nominatim geocoding
    2. Get NWS grid points for those coordinates
    3. Fetch the forecast and extract current temperature
    """
    try:
        # Step 1: Get coordinates from city/state using Nominatim
        geocode_url = 'https://nominatim.openstreetmap.org/search'
        location_query = f"{city}, {state}, USA" if state else f"{city}, USA"
        params = {
            'q': location_query,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'WeatherApp/1.0'  # Required by Nominatim
        }

        geo_response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            print(f"Could not find coordinates for {city}")
            return None

        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        print(f"Found coordinates for {city}: {lat}, {lon}")

        # Step 2: Get NWS grid points
        points_url = f'https://api.weather.gov/points/{lat},{lon}'
        points_headers = {
            'User-Agent': 'WeatherApp/1.0',
            'Accept': 'application/json'
        }

        points_response = requests.get(points_url, headers=points_headers, timeout=10)
        points_response.raise_for_status()
        points_data = points_response.json()

        forecast_url = points_data['properties']['forecast']
        print(f"Forecast URL: {forecast_url}")

        # Step 3: Get the forecast
        forecast_response = requests.get(forecast_url, headers=points_headers, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # Extract current temperature from the first period
        current_temp = forecast_data['properties']['periods'][0]['temperature']
        print(f"Current temperature for {city}: {current_temp}°F")

        return float(current_temp)

    except requests.exceptions.RequestException as e:
        print(f"API request failed for {city}: {e}")
        return None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error parsing API response for {city}: {e}")
        return None
