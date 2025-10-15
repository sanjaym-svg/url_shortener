from flask import Flask, request, redirect, render_template
import pymysql
import hashlib, base64

# Database Config
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="@Mysql67",
        database="test",
        cursorclass=pymysql.cursors.DictCursor
    )

app = Flask(__name__)

# Generate short URL
def generate_short_url(long_url):
    hash_object = hashlib.sha256(long_url.encode())
    short_hash = base64.urlsafe_b64encode(hash_object.digest())[:6].decode()
    return short_hash

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.form.get('long_url')
    if not long_url:
        return "Invalid URL", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT short_url FROM url_mapping WHERE long_url=%s", (long_url,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return f"Shortened URL: <a href='{request.host_url}{existing['short_url']}'>{request.host_url}{existing['short_url']}</a>"

    short_url = generate_short_url(long_url)
    cursor.execute("INSERT INTO url_mapping (long_url, short_url) VALUES (%s, %s)", (long_url, short_url))
    conn.commit()
    conn.close()
    return f"Shortened URL: <a href='{request.host_url}{short_url}'>{request.host_url}{short_url}</a>"

@app.route('/<short_url>')
def redirect_url(short_url):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT long_url FROM url_mapping WHERE short_url=%s", (short_url,))
    entry = cursor.fetchone()
    if entry:
        cursor.execute("UPDATE url_mapping SET clicks=clicks+1 WHERE short_url=%s", (short_url,))
        conn.commit()
        conn.close()
        return redirect(entry['long_url'])

    conn.close()
    return "Error: URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
