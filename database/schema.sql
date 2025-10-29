-- Database Schema for Flask Starter Kit
-- Run this file to create the required database structure

-- Create sample_table
CREATE TABLE sample_table (
    sample_table_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Add indexes for common queries
CREATE INDEX idx_sample_table_name ON sample_table (last_name, first_name);
CREATE INDEX idx_sample_table_dob ON sample_table (date_of_birth);

-- Create tickers table
CREATE TABLE tickers (
    ticker_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Add index for ticker symbol lookups
CREATE INDEX idx_tickers_symbol ON tickers (symbol);

-- Create weather table
CREATE TABLE weather (
    weather_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    temperature DECIMAL(5, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Add index for city lookups
CREATE INDEX idx_weather_city ON weather (city);