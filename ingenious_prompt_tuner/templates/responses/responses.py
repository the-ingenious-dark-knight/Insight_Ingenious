from flask import (
    Blueprint,
    Response,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    stream_with_context,
    url_for,
    current_app,
    jsonify,
)
import asyncio
import yaml
import json
import uuid as guid
from ingenious_prompt_tuner.event_processor import functional_tests
import subprocess
import markdown
from pathlib import Path
import ingenious_prompt_tuner.payload as rp1
from ingenious_prompt_tuner.utilities import (
    requires_auth,
    requires_selected_revision,
    utils_class,
    get_selected_revision_direct_call,
)

# Authentication Helpers

bp = Blueprint("responses", __name__, url_prefix="/responses")


# Routes
@bp.route("/list")
@requires_auth
@requires_selected_revision
def list():
    return render_template("responses/view_responses.html")


@bp.route("/get_test_data_files", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_test_data_files():
    utils: utils_class = current_app.utils
    output_path = (
        current_app.config["test_output_path"]
        + f"/{get_selected_revision_direct_call()}"
    )
    files_all = asyncio.run(utils.fs.list_files(file_path=output_path))
    if files_all:
        files = [f for f in files_all if f.endswith(".json") and f.startswith("data_")]
        files.sort(
            key=lambda x: json.loads(
                asyncio.run(utils.fs.read_file(file_name=x, file_path=output_path))
            )["identifier"]
        )
    else:
        files = []

    if files_all:
        files = [f for f in files_all if f.endswith(".json") and f.startswith("data_")]
    else:
        files = []

    return jsonify({"files": files})


@bp.route("/get_payload", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_payload():
    utils: utils_class = current_app.utils
    identifier = request.args.get("identifier", type=str)
    event_type = request.args.get("event_type", type=str)
    output_dir = (
        current_app.config["test_output_path"]
        + f"/{get_selected_revision_direct_call()}"
    )
    return asyncio.run(
        rp1.render_payload(identifier, utils.fs, output_dir, event_type)
    )


@bp.route("/rerun_event", methods=["GET"])
@requires_auth
@requires_selected_revision
def rerun_event():
    utils: utils_class = current_app.utils
    ft = functional_tests(config=current_app.config)
    agents = current_app.config["agents"] 
    try:
        identifier = request.args.get("identifier", type=str)
        event_type = request.args.get("event_type", type=str)
        file_name = request.args.get("file_name", type=str)
        asyncio.run(
            ft.run_event_from_pre_processed_file(
                identifier=identifier,
                event_type=event_type,
                file_name=file_name,
                revision_id=get_selected_revision_direct_call(),
                agents=agents
            )
        )

    except ValueError:
        return "Failed"

    # return success
    return "Succeeded"


@bp.route("/get_agent_response", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_agent_response():
    utils: utils_class = current_app.utils
    identifier = request.args.get("identifier", type=str)
    event_type = request.args.get("event_type", type=str)
    agent_name = request.args.get("agent_name", type=str)
    # Return mock html page
    file_name = f"agent_response_{event_type}_{agent_name}_{identifier.strip()}.md"
    output_path = (
        current_app.config["test_output_path"]
        + f"/{get_selected_revision_direct_call()}"
    )
    agent_response_md = asyncio.run(
        utils.fs.read_file(file_name=file_name, file_path=output_path)
    )
    agent_response_md1 = render_template(
        "responses/agent_response.html", agent_response=agent_response_md
    )
    html_content = markdown.markdown(
        agent_response_md1,
        extensions=["extra", "md_in_html", "toc", "fenced_code", "codehilite"],
    )
    return html_content


@bp.route("/get_responses", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_responses():
    utils: utils_class = current_app.utils
    agents = current_app.config["agents"]
    try:
        output_path = (
            current_app.config["test_output_path"]
            + f"/{get_selected_revision_direct_call()}"
        )
        if asyncio.run(
            utils.fs.check_if_file_exists(file_name="events.yml", file_path=output_path)
        ):
            files = yaml.safe_load(
                asyncio.run(
                    utils.fs.read_file(file_name="events.yml", file_path=output_path)
                )
            )
        else:
            return "<p>No responses folder found.</p>"

    except ValueError:
        return "<p>No responses folder found.</p>"

    # render the responses2.html file
    return render_template("responses/responses2.html", files=files, agents=agents)


@bp.route("/get_agent_response_from_file", methods=["post"])
@requires_auth
@requires_selected_revision
def get_agent_response_from_file():
    utils: utils_class = current_app.utils
    identifier = request.form.get("identifier", type=str).replace("#", "")
    event_type = request.form.get("event_type", type=str)

    file_name = f"agent_response_{event_type}_summary_agent_{identifier.strip()}.md"
    output_path = (
        current_app.config["test_output_path"]
        + f"/{get_selected_revision_direct_call()}"
    )
    file_contents = asyncio.run(
        utils.fs.read_file(file_name=file_name, file_path=output_path)
    )
    if file_contents is None:
        return "No response found"
    html_content = markdown.markdown(
        file_contents,
        extensions=["extra", "md_in_html", "toc", "fenced_code", "codehilite"],
    )
    return html_content


@bp.route("/run_live_progress", methods=["GET"])
@requires_auth
@requires_selected_revision
def run_live_progress():
    utils: utils_class = current_app.utils
    max_processed_events = request.args.get("max_processed_events", default=1, type=int)

    def generate():
        process = subprocess.Popen(
            args=[
                "ingen_cli",
                "run-test-batch",
                "--run-args",
                f"--max_processed_events={max_processed_events} --test_run_session_id={get_selected_revision_direct_call()}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered
        )
        try:
            for line in iter(process.stdout.readline, ""):
                if line:
                    # from ansi2html import Ansi2HTMLConverter
                    # conv = Ansi2HTMLConverter()
                    # ansi = line
                    # html = conv.convert(ansi, full=False)
                    html = line
                    yield f"data: {html}\n\n"
            process.stdout.close()
            process.wait()

            if process.returncode == 0:
                yield "event: complete\ndata: Tests completed successfully.\n\n"
            else:
                yield f"data: Error occurred: MPE{max_processed_events} --- {process.stderr.read().strip()}\n\n"
        except Exception as e:
            yield f"data: Error occurred: MPE{max_processed_events} --- {str(e)}\n\n"
        finally:
            process.terminate()

    return Response(stream_with_context(generate()), content_type="text/event-stream")
