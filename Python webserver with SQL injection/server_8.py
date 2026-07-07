import http.server
import socketserver
import ssl
import urllib.parse
import sqlite3

PORT = 9000
HANDLER = http.server.BaseHTTPRequestHandler

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

class CustomHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        response = """
        <html>
            <body>
                <h2>Login</h2>
                <form method="POST" action="/login">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required><br>
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required><br>
                    <button type="submit">Login</button>
                </form>
            </body>
        </html>
        """
        self.wfile.write(response.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = urllib.parse.parse_qs(post_data.decode("utf-8"))

        username = post_data.get("username", [None])[0]
        password = post_data.get("password", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        # Vulnerable to SQL injection
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"Executing query: {query}")  # Debugging line
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            response = f"<h1>Welcome, {username}!</h1>"
        else:
            self.send_response(401)
            response = "<h1>HTTP 401 Unauthorized</h1>"

        self.wfile.write(response.encode("utf-8"))

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Server Started At: https://localhost:{PORT}")
    httpd.serve_forever()
