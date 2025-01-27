from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)
import asyncio
import yaml
import uuid as guid
from pathlib import Path
import os
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback
from ingenious_prompt_tuner.utilities import (
    requires_auth,
    utils_class,
    get_selected_revision_direct_call,
)

# Authentication Helpers

bp = Blueprint("index", __name__)


# Routes


@bp.route("/")
@requires_auth
def home():
    class Revision:
        def __init__(self, description):
            self.name = guid.uuid4()
            self.description

    utils: utils_class = current_app.utils
    if asyncio.run(
        utils.fs.check_if_file_exists(
            file_name="revisions.yml",
            file_path=str(current_app.config["revisions_folder"]),
        )
    ):
        revisions_str = asyncio.run(
            utils.fs.read_file(
                file_name="revisions.yml",
                file_path=str(current_app.config["revisions_folder"]),
            )
        )
        revisions = yaml.safe_load(revisions_str)
    else:
        return redirect(url_for("index.create_revision"))

    return render_template("home.html", files=revisions)


@bp.route("/create_revision", methods=["GET", "POST"])
@requires_auth
def create_revision():
    utils: utils_class = current_app.utils
    if request.method == "POST":
        revision_name = request.form["revision_name"]
        revision_description = request.form["revision_description"]
        new_revision = {"name": revision_name, "description": revision_description}
        REVISIONS_FOLDER = current_app.config["revisions_folder"]

        if asyncio.run(
            utils.fs.check_if_file_exists(
                file_name="revisions", file_path=str(REVISIONS_FOLDER)
            )
        ):
            revisions_str = asyncio.run(
                utils.fs.read_file(
                    file_name="revisions", file_path=str(REVISIONS_FOLDER)
                )
            )
            revisions = yaml.safe_load(revisions_str)
        else:
            revisions = []

        revisions.append(new_revision)
        revisions_str = yaml.safe_dump(revisions)
        asyncio.run(
            utils.fs.write_file(
                contents=revisions_str,
                file_name="revisions",
                file_path=str(REVISIONS_FOLDER),
            )
        )
        prompts = asyncio.run(
            utils.fs.list_files(f"prompts/{get_selected_revision_direct_call()}")
        )
        function_test_outputs = asyncio.run(
            utils.fs.list_files(
                f"functional_test_outputs/{get_selected_revision_direct_call()}"
            )
        )

        for prompt in prompts:
            content = asyncio.run(
                utils.fs.read_file(
                    file_name=prompt,
                    file_path=f"prompts/{get_selected_revision_direct_call()}",
                )
            )
            asyncio.run(
                utils.fs.write_file(
                    file_name=prompt,
                    file_path=f"prompts/{revision_name}",
                    contents=content,
                )
            )

        for function_test_output in function_test_outputs:
            content = asyncio.run(
                utils.fs.read_file(
                    file_name=prompt,
                    file_path=f"functional_test_outputs/{get_selected_revision_direct_call()}",
                )
            )
            asyncio.run(
                utils.fs.write_file(
                    file_name=prompt,
                    file_path=f"functional_test_outputs/{revision_name}",
                    contents=content,
                )
            )

        return redirect(url_for("index.home"))
    return render_template("revisions/create_revision.html")


@bp.route('/save_revision', methods=['POST'])
@requires_auth
def save_revision():
    utils: utils_class = current_app.utils
    revision_name = str(guid.uuid4())
    revision_description = request.form['revision_description']
    new_revision = {'name': revision_name, 'description': revision_description}
    file_path_old_outputs = f"functional_test_outputs/{revision_name}"   
    file_path_revisions = "revisions"
    file_path_old_prompts = f"prompts/{revision_name}"

    file_path_new_outputs = f"functional_test_outputs/{revision_name}"
    file_path_new_prompts = f"prompts/{revision_name}"

    if asyncio.run(utils.fs.check_if_file_exists(file_name='revisions.yml', file_path=file_path_revisions)):
        revisions_str = asyncio.run(utils.fs.read_file(file_name='revisions.yml', file_path=str(file_path_revisions)))
        revisions = yaml.safe_load(revisions_str)
    else:
        revisions = []

    revisions.append(new_revision)
    revisions_str = yaml.safe_dump(revisions)
    asyncio.run(utils.fs.write_file(contents=revisions_str, file_name='revisions.yml', file_path=str(file_path_revisions)))
    
    # Make sure that the prompts and sample data files are copied to the new revision folder
    asyncio.run(utils.get_functional_tests_folder(new_revision["name"]))
    asyncio.run(utils.get_prompt_template_folder(new_revision["name"]))
    

    return redirect(url_for('index.home'))
