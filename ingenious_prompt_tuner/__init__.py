import asyncio
import os
import ingenious.dependencies as ig_deps
from ingenious.models.test_data import Events
import ingenious_prompt_tuner.utilities as uti
from flask import Flask
from functools import wraps
from pathlib import Path
from ingenious.utils.namespace_utils import import_class_with_fallback, get_path_from_namespace_with_fallback
from ingenious.models.agent import AgentChats, Agents, IProjectAgents
from ingenious_prompt_tuner.templates import home
from ingenious_prompt_tuner.templates.responses import responses
from ingenious_prompt_tuner.templates.prompts import prompts
from ingenious_prompt_tuner import auth

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

    # Set utils so that downstream blueprints have access to the config
    app.utils = uti.utils_class(config)
    
    # Get the list of agents -- note this should preference the Agents class in the project level extensions dir
    # Note the Agents module and ProjectAgents class must be defined in the project level extensions dir
    agents_class: IProjectAgents = import_class_with_fallback('models.agent', "ProjectAgents")
    agents_instance = agents_class()
    agents: Agents = agents_instance.Get_Project_Agents(config)

    app.config["agents"] = agents
    app.config["test_output_path"] = str(Path("functional_test_outputs"))   

    # ensure the instance folder exists
    try:
        # os.makedirs(app.instance_path)
        print(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(prompts.bp)
    app.register_blueprint(responses.bp)

    return app
