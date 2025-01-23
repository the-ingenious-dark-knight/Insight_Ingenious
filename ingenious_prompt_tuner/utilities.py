import json
from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response, stream_with_context
from functools import wraps 
from ingenious.files.files_repository import FileStorage


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def requires_selected_revision(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        selected_revision = request.cookies.get('selected_revision')
        if not selected_revision:
            return redirect(url_for('index.home'))
        return f(*args, **kwargs)
    return decorated_function


def get_selected_revision_direct_call():
    selected_revision = request.cookies.get('selected_revision')
    if selected_revision:
        return selected_revision
    return None


class utils_class:
    def __init__(self, config):
        self.fs = FileStorage(config)

    def read_file(self, file_name, file_path):
        self.fs.read_file(file_name=file_name, file_path=file_path)

    

                    
