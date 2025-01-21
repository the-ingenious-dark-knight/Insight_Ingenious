import os
import ingenious.dependencies as ig_deps
import ingenious_prompt_tuner.utilities as uti
from flask import Flask
from functools import wraps
from pathlib import Path

config = ig_deps.get_config()


def hw():
    return "Hello World"


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
        template_folder="templates",
    )

    app.secret_key = config.web_configuration.authentication.password
    app.config["username"] = config.web_configuration.authentication.username
    app.config["password"] = config.web_configuration.authentication.password
    app.config["revisions_folder"] = str(Path("revisions"))
    app.config["prompt_template_folder"] = os.path.join(
        "ingenious_extensions", "templates", "prompts"
    )
    app.config["test_output_path"] = str(Path("functional_test_outputs"))

    app.utils = uti.utils_class(config)

    # ensure the instance folder exists
    try:
        # os.makedirs(app.instance_path)
        print(app.instance_path)
    except OSError:
        pass

    from . import auth, index, prompts, responses

    app.register_blueprint(auth.bp)
    app.register_blueprint(index.bp)
    app.register_blueprint(prompts.bp)
    app.register_blueprint(responses.bp)

    return app
