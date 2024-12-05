import json
import glob
import os
import traceback
import yaml
from jinja2 import Environment, FileSystemLoader, TemplateError
from livereload import Server

def load_data():
    """Load all JSON and YAML files from the data/ directory and return a single dictionary."""
    data = {}

    # Load JSON files, handling .json and .JSON file extensions.
    for json_file in glob.glob('data/*.[jJ][sS][oO][nN]'):
        try:
            with open(json_file, 'r') as f:
                data.update(json.load(f))
            print(f'Loaded data from {json_file}')
        except Exception as e:
            print(f'Error loading data from {json_file}: {e}')
            traceback.print_exc()

    # Load YAML files, handling .yaml and .YAML extensions.
    for yaml_file in glob.glob('data/*.[yY][aA][mM][lL]'):
        try:
            with open(yaml_file, 'r') as f:
                data.update(yaml.safe_load(f))
            print(f'Loaded data from {yaml_file}')
        except Exception as e:
            print(f'Error loading data from {yaml_file}: {e}')
            traceback.print_exc()

    return data

def render_all_templates(env, data, trigger_file=None):
    """Render all templates, excluding partials."""

    if trigger_file:
        print(f'>>> Rebuild triggered by change in: {trigger_file}')

    if not os.path.exists('site'):
        os.makedirs('site')

    # Collect templates from templates/ directory, excluding partials
    template_files = [f for f in glob.glob('templates/**/*.j2', recursive=True) if 'partials' not in f]

    for template_path in template_files:
        try:
            template = env.get_template(os.path.relpath(template_path, 'templates'))
            output = template.render(data)
            outname = os.path.join('site', os.path.relpath(template_path, 'templates').replace('.html.j2', '.html').replace('.j2', '.html'))
            outdir = os.path.dirname(outname)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            with open(outname, 'w') as out:
                out.write(output)
            print(f'Rendered {template_path} to {outname}')
        except TemplateError as e:
            print(f'Error rendering {template_path}: {e}')
            traceback.print_exc()
        except Exception as e:
            print(f'Unexpected error rendering {template_path}: {e}')
            traceback.print_exc()


def render_all(trigger_file=None):
    env = Environment(loader=FileSystemLoader('templates'))
    data = load_data()
    render_all_templates(env, data, trigger_file)

if __name__ == "__main__":
    render_all()

    server = Server()
    server.watch('templates/**/*.j2', lambda path: render_all(path))
    server.watch('data/*.json', lambda path: render_all(path))
    server.watch('data/*.[yY][aA][mM][lL]', lambda path: render_all(path))
    server.serve(root='site')
