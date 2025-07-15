# schema.sql
CREATE DATABASE IF NOT EXISTS custom_search;

USE custom_search;

CREATE TABLE IF NOT EXISTS search_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query VARCHAR(255),
    title TEXT,
    url TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
