import os
import subprocess
from flask import Flask, render_template_string, request, redirect, url_for, jsonify, session, send_file
from functools import wraps
import sys
import io

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(parent_dir)
import ingenious.dependencies as ig_deps

app = Flask(__name__)

app.secret_key = ig_deps.config.web_configuration.authentication.password

TEMPLATE_FOLDER = os.path.join(parent_dir, 'templates', 'prompts')

output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
functional_test_dir = os.path.join(output_dir, 'functional_test_outputs')

# Simple username and password
USERNAME = ig_deps.config.web_configuration.authentication.username
PASSWORD = ig_deps.config.web_configuration.authentication.password
PORT = ig_deps.config.web_configuration.port
HOST = ig_deps.config.web_configuration.ip_address


def check_auth(username, password):
    """Check if a username/password combination is valid."""
    return username == USERNAME and password == PASSWORD


def authenticate():
    """Send a 401 response that enables basic auth."""
    return jsonify({"status": "error", "output": "Authentication required"}), 401


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_auth(username, password):
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return "Invalid credentials", 401
    return render_template_string("""
        <form method="post">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username"><br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    """)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/')
@requires_auth
def home():
    html = ""
    with open(os.path.join(os.path.dirname(__file__), './flask_app_index.html'), 'r') as f:
        html = f.read()

    try:
        files = sorted([f for f in os.listdir(TEMPLATE_FOLDER) if f.endswith(('.md', '.jinja'))])
    except FileNotFoundError:
        files = []

    return render_template_string(html, files=files)


@app.route('/get_responses', methods=['GET'])
@requires_auth
def get_responses():
    """Route to read the responses.html file server-side and return its contents."""
    latest_folder = max(
        [os.path.join(functional_test_dir, d) for d in os.listdir(functional_test_dir)],
        key=os.path.getmtime
    )
    print(latest_folder)
    RESPONSES_FILE = os.path.join(latest_folder, 'responses.html')

    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as rf:
            return rf.read()
    return "<p>No responses found or file does not exist.</p>"


@app.route('/download_responses', methods=['GET'])
@requires_auth
def download_responses():
    """Route to download the responses.html file."""
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as rf:
            file_contents = rf.read()
        return send_file(
            io.BytesIO(file_contents.encode('utf-8')),
            as_attachment=True,
            download_name='responses.html',
            mimetype='text/html'
        )
    return jsonify({"status": "error", "output": "Responses file not found"}), 404


@app.route('/run_simple_tests', methods=['POST'])
@requires_auth
def run_simple_tests():
    """Route to run tests/run_local_test_simple.py."""
    try:
        result = subprocess.run(
            ["ingen_cli", "run-test-batch"],
            capture_output=True,
            text=True,
            check=False
        )
        status = "success" if result.returncode == 0 else "error"
        return jsonify({"status": status, "output": result.stdout or result.stderr})
    except Exception as e:
        return jsonify({"status": "error", "output": str(e)})


@app.route('/edit/<filename>', methods=['GET', 'POST'])
@requires_auth
def edit_file(filename):
    file_path = os.path.join(TEMPLATE_FOLDER, filename)
    if request.method == 'POST':
        new_content = request.form.get('file_content', '')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return redirect(url_for('home'))
    else:
        if not os.path.exists(file_path):
            return f"File '{filename}' does not exist.", 404
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Editing: {filename}</title>
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
                </head>
                <body class="p-3">
                    <div class="container">
                        <h1>Editing: {filename}</h1>
                        <form method="POST">
                            <textarea name="file_content" rows="25" class="form-control">{content}</textarea>
                            <br>
                            <button type="submit" class="btn btn-primary">Save</button>
                            <a href="{url_for('home')}" class="btn btn-secondary">Back</a>
                        </form>
                    </div>
                </body>
                </html>
                """
        return html


if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
