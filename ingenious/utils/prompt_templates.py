import os
from jinja2 import Environment, FileSystemLoader

# Get the absolute path to the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the "templates/prompts" directory relative to the script directory
template_path = os.path.join(script_dir, "templates", "prompts")

# Set up the Jinja2 environment
env = Environment(loader=FileSystemLoader(template_path), autoescape=True)

# Load templates
system_prompt_template = env.get_template("system_prompt.jinja")
follow_up_prompt_template = env.get_template("follow_up_prompt.jinja")
