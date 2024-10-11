from flask import Flask
import redis
import psycopg2
import os

app = Flask(__name__)

# Redis connection
r = redis.Redis(host="redis", port=6379)

# PostgreSQL connection
def get_db_connection():
    conn = psycopg2.connect(
        host="db",  # Hostname of the PostgreSQL service from docker-compose
        database="flaskdb",
        user="flaskuser",
        password="flaskpass"
    )
    return conn

@app.route("/")
def home():
    # Increment Redis counter
    count = r.incr("hits")

    # Save the count to PostgreSQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO visits (visit_count) VALUES (%s)", (count,))
    conn.commit()

    # Fetch total visit count from PostgreSQL
    cursor.execute("SELECT COUNT(*) FROM visits;")
    total_visits = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return f"This page has been visited {count} times.<br>Total visits recorded in PostgreSQL: {total_visits}"

if __name__ == "__main__":
    app.run(host="0.0.0.0")
