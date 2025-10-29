from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db_connect import get_db
import yfinance as yf

tickers_bp = Blueprint('tickers', __name__)

@tickers_bp.route('/tickers')
def index():
    """Display all tickers from database"""
    connection = get_db()
    result = []
    edit_ticker = None
    delete_ticker = None

    edit_id = request.args.get('edit_id')
    delete_id = request.args.get('delete_id')

    if connection is None:
        flash("Database connection failed. Please check your database configuration.", "error")
    else:
        try:
            if edit_id:
                query = "SELECT * FROM tickers WHERE ticker_id = %s"
                with connection.cursor() as cursor:
                    cursor.execute(query, (edit_id,))
                    edit_ticker = cursor.fetchone()

            if delete_id:
                query = "SELECT * FROM tickers WHERE ticker_id = %s"
                with connection.cursor() as cursor:
                    cursor.execute(query, (delete_id,))
                    delete_ticker = cursor.fetchone()

            query = "SELECT * FROM tickers ORDER BY symbol"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
        except Exception as e:
            flash(f"Database error: {e}", "error")
            result = []

    return render_template("tickers.html", tickers=result, edit_ticker=edit_ticker, delete_ticker=delete_ticker)


@tickers_bp.route('/tickers/add', methods=['POST'])
def add_ticker():
    """Add new ticker to database - Auto-increment ticker_id"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('tickers.index'))

    symbol = request.form.get('symbol', '').upper().strip()
    name = request.form.get('name', '').strip()
    price = request.form.get('price', type=float, default=0.0)

    if not symbol or not name:
        flash("Symbol and name are required.", "error")
        return redirect(url_for('tickers.index'))

    try:
        query = """
        INSERT INTO tickers (symbol, name, price)
        VALUES (%s, %s, %s)
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (symbol, name, price))
        connection.commit()

        flash(f"Ticker {symbol} added successfully!", "success")
    except Exception as e:
        flash(f"Error adding ticker: {e}", "error")

    return redirect(url_for('tickers.index'))


@tickers_bp.route('/tickers/update/<int:ticker_id>')
def update_price(ticker_id):
    """Fetch live price from API and update database with new price"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('tickers.index'))

    try:
        # First, get the ticker symbol from database
        query = "SELECT symbol FROM tickers WHERE ticker_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (ticker_id,))
            ticker = cursor.fetchone()

        if not ticker:
            flash("Ticker not found.", "error")
            return redirect(url_for('tickers.index'))

        symbol = ticker['symbol']

        # Fetch live price from API
        live_price = fetch_live_price(symbol)

        if live_price is None:
            flash(f"Could not fetch live price for {symbol}.", "error")
            return redirect(url_for('tickers.index'))

        # Update database with new price
        update_query = """
        UPDATE tickers
        SET price = %s
        WHERE ticker_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(update_query, (live_price, ticker_id))
        connection.commit()

        flash(f"Price updated for {symbol}: ${live_price:.2f}", "success")

    except Exception as e:
        flash(f"Error updating price: {e}", "error")

    return redirect(url_for('tickers.index'))


@tickers_bp.route('/tickers/edit/<int:ticker_id>', methods=['POST'])
def edit_ticker(ticker_id):
    """Edit existing ticker"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('tickers.index'))

    symbol = request.form.get('symbol', '').upper().strip()
    name = request.form.get('name', '').strip()
    price = request.form.get('price', type=float, default=0.0)

    if not symbol or not name:
        flash("Symbol and name are required.", "error")
        return redirect(url_for('tickers.index'))

    try:
        query = """
        UPDATE tickers
        SET symbol = %s, name = %s, price = %s
        WHERE ticker_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (symbol, name, price, ticker_id))
        connection.commit()

        flash(f"Ticker {symbol} updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating ticker: {e}", "error")

    return redirect(url_for('tickers.index'))


@tickers_bp.route('/tickers/delete/<int:ticker_id>', methods=['POST'])
def delete_ticker(ticker_id):
    """Delete ticker"""
    connection = get_db()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('tickers.index'))

    try:
        query = "DELETE FROM tickers WHERE ticker_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (ticker_id,))
        connection.commit()

        flash("Ticker deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting ticker: {e}", "error")

    return redirect(url_for('tickers.index'))


def fetch_live_price(symbol):
    """
    Fetch live price from Yahoo Finance using yfinance library
    Always use the latest version: pip install yfinance --upgrade
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.info

        # Try to get current price (prioritize currentPrice, fallback to regularMarketPrice)
        price = data.get('currentPrice') or data.get('regularMarketPrice')

        if price:
            return float(price)
        else:
            print(f"No price data available for {symbol}")
            return None

    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None
