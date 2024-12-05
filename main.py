from http import server
from guizero import App, PushButton, TextBox, Box
from version import app_name, version, release_date
import json
import glob
import os
import traceback
import yaml
from jinja2 import Environment, FileSystemLoader, TemplateError
from livereload import Server
from datetime import datetime


def load_data():
    """Load all JSON and YAML files from the data/ directory and return a single dictionary."""
    data = {}

    # Load JSON files, handling .json and .JSON file extensions.
    for json_file in glob.glob('data/*.[jJ][sS][oO][nN]'):
        try:
            with open(json_file, 'r') as f:
                data.update(json.load(f))
            output_status(f'Loaded data from {json_file}')
        except Exception as e:
            output_status(f'Error loading data from {json_file}: {e}')
            traceback.print_exc()

    # Load YAML files, handling .yaml and .YAML extensions.
    for yaml_file in glob.glob('data/*.[yY][aA][mM][lL]'):
        try:
            with open(yaml_file, 'r') as f:
                data.update(yaml.safe_load(f))
            output_status(f'Loaded data from {yaml_file}')
        except Exception as e:
            output_status(f'Error loading data from {yaml_file}: {e}')
            traceback.print_exc()

    return data


def render_all_templates(env, data, trigger_file=None):
    """Render all templates, excluding partials."""

    if trigger_file:
        output_status(f'>>> Rebuild triggered by change in: {trigger_file}')

    if not os.path.exists('build'):
        os.makedirs('build')

    # Collect templates from templates/ directory, excluding partials
    template_files = [f for f in glob.glob('templates/**/*.j2', recursive=True) if 'partials' not in f]

    for template_path in template_files:
        try:
            template = env.get_template(os.path.relpath(template_path, 'templates'))
            output = template.render(data)
            outname = os.path.join('build', os.path.relpath(template_path, 'templates').replace('.html.j2', '.html').replace('.j2', '.html'))
            outdir = os.path.dirname(outname)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            with open(outname, 'w') as out:
                out.write(output)
            output_status(f'Rendered {template_path} to {outname}')
        except TemplateError as e:
            output_status(f'Error rendering {template_path}: {e}')
            traceback.print_exc()
        except Exception as e:
            output_status(f'Unexpected error rendering {template_path}: {e}')
            traceback.print_exc()


def render_all(trigger_file=None):
    env = Environment(loader=FileSystemLoader('templates'))
    data = load_data()
    render_all_templates(env, data, trigger_file)


def output_status(message_text):
    """Output a status message to the output box."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message_text = f'{now} | {message_text}'
    output_message_box.append(message_text)
    # Scroll to the end of the output box, via a TK call to the underlying widget.
    # (resolves a performance issue in GUIZero, but also shows us the bit we want.)
    output_message_box.tk.see('end')


def exit_app():
    """Exit the application."""
    app.destroy()

def clear_output():
    """Clear the output box."""
    output_message_box.clear()


if __name__ == "__main__":
    version_string = f">>> {app_name} v{version}, {release_date}"
    app = App(title=app_name, width=740, height=600, layout="auto")

    output_box = Box(app)
    output_message_box = TextBox(output_box, align="left", width=98, height=38, multiline=True, scrollbar=True, text=version_string)

    button_box = Box(app)
    button = PushButton(button_box, align="left", command=exit_app, text="Quit", width=20, height=3)
    button = PushButton(button_box, align="left", command=clear_output, text="Clear Output", width=20, height=3)
    # button = PushButton(button_box, align="left", command=render_all, text="Go!", width=20, height=3)

    render_all()
    server = Server()
    server.watch('templates/**/*.j2', lambda path: render_all(path))
    server.watch('data/*.json', lambda path: render_all(path))
    server.watch('data/*.[yY][aA][mM][lL]', lambda path: render_all(path))
    server.serve(root='build')

    app.display()
