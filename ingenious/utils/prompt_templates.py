import os
from jinja2 import Environment, FileSystemLoader

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader(os.path.join("templates", "prompts")), autoescape=True)

# Load templates
system_prompt_template = env.get_template("system_prompt.jinja")
follow_up_prompt_template = env.get_template("follow_up_prompt.jinja")
