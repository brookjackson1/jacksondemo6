import requests

def test_atlanta_weather():
    """Test fetching weather for Atlanta, Georgia"""

    city = "Atlanta"
    state = "Georgia"

    print(f"Testing weather fetch for {city}, {state}")
    print("=" * 60)

    try:
        # Step 1: Get coordinates from city/state using Nominatim
        print("\n[STEP 1] Geocoding...")
        geocode_url = 'https://nominatim.openstreetmap.org/search'
        location_query = f"{city}, {state}, USA"
        params = {
            'q': location_query,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'WeatherApp/1.0'
        }

        geo_response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
        print(f"Geocoding status: {geo_response.status_code}")
        geo_data = geo_response.json()

        if not geo_data:
            print("[ERROR] No geocoding results found")
            return

        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        print(f"[SUCCESS] Coordinates: {lat}, {lon}")

        # Step 2: Get NWS grid points
        print("\n[STEP 2] Getting NWS grid points...")
        points_url = f'https://api.weather.gov/points/{lat},{lon}'
        points_headers = {
            'User-Agent': 'WeatherApp/1.0',
            'Accept': 'application/json'
        }

        points_response = requests.get(points_url, headers=points_headers, timeout=10)
        print(f"NWS Points status: {points_response.status_code}")

        if points_response.status_code != 200:
            print(f"[ERROR] NWS Points failed: {points_response.text}")
            return

        points_data = points_response.json()

        if 'properties' not in points_data:
            print(f"[ERROR] No properties in response: {points_data}")
            return

        forecast_url = points_data['properties']['forecast']
        print(f"[SUCCESS] Forecast URL: {forecast_url}")

        # Step 3: Get the forecast
        print("\n[STEP 3] Getting forecast...")
        forecast_response = requests.get(forecast_url, headers=points_headers, timeout=10)
        print(f"Forecast status: {forecast_response.status_code}")

        if forecast_response.status_code != 200:
            print(f"[ERROR] Forecast failed: {forecast_response.text}")
            return

        forecast_data = forecast_response.json()

        if 'properties' not in forecast_data or 'periods' not in forecast_data['properties']:
            print(f"[ERROR] Invalid forecast structure")
            return

        periods = forecast_data['properties']['periods']
        if periods:
            current_temp = periods[0]['temperature']
            period_name = periods[0]['name']
            print(f"[SUCCESS] {period_name} Temperature: {current_temp}°F")
            print(f"[SUCCESS] Short Forecast: {periods[0]['shortForecast']}")
        else:
            print("[ERROR] No forecast periods available")

    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_atlanta_weather()
