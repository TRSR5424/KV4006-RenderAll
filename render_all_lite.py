import glob
import json
import os
import shutil
import traceback
import time

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def load_data():
    """Load all JSON and YAML files from the data/ directory and return a single dictionary."""
    data = {}

    # Load JSON files, handling .json and .JSON file extensions.
    for json_file in glob.glob("data/*.[jJ][sS][oO][nN]"):
        try:
            with open(json_file, "r") as f:
                data.update(json.load(f))
            print(f"Loaded data from {json_file}")
        except Exception as e:
            print(f"Error loading data from {json_file}: {e}")
            traceback.print_exc()

    # Load YAML files, handling .yaml and .YAML extensions.
    for yaml_file in glob.glob("data/*.[yY][aA][mM][lL]"):
        try:
            with open(yaml_file, "r") as f:
                data.update(yaml.safe_load(f))
            print(f"Loaded data from {yaml_file}")
        except Exception as e:
            print(f"Error loading data from {yaml_file}: {e}")
            traceback.print_exc()

    return data


def copy_html_files():
    """Copy .html files from templates/ to site/ without parsing them."""
    if not os.path.exists("site"):
        os.makedirs("site")

    for html_file in glob.glob("templates/**/*.html", recursive=True):
        try:
            destination = os.path.join("site", os.path.relpath(html_file, "templates"))
            outdir = os.path.dirname(destination)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            if os.path.exists(destination):
                os.remove(destination)
            shutil.copy(html_file, destination)
            print(f"Copied {html_file} to {destination}")
        except Exception as e:
            print(f"Error copying {html_file} to {destination}: {e}")
            traceback.print_exc()


def render_all_templates(env, data, trigger_file=None):
    """Render all templates, excluding partials."""

    if trigger_file:
        print(f">>> Rebuild triggered by change in: {trigger_file}")
        if trigger_file.endswith(".html"):
            copy_html_files()
            return

    if not os.path.exists("site"):
        os.makedirs("site")

    # Collect templates from templates/ directory, excluding partials
    template_files = [
        f
        for f in glob.glob(os.path.join("templates", "**", "*.*"), recursive=True)
        if f.endswith((".j2", ".jinja")) and "partials" not in f
    ]

    for template_path in template_files:
        try:
            template_rel_path = os.path.relpath(template_path, "templates").replace(os.sep, "/")
            template = env.get_template(template_rel_path)
            output = template.render(data)
            outname = os.path.join(
                "site",
                os.path.normpath(template_rel_path)
                .replace(".html.j2", ".html")
                .replace(".j2", ".html")
                .replace(".html.jinja", ".html")
                .replace(".jinja", ".html"),
            )
            outdir = os.path.dirname(outname)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            with open(outname, "w") as out:
                out.write(output)
            print(f"Rendered {template_path} to {outname}")
        except TemplateError as e:
            print(f"Error rendering {template_path}: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"Unexpected error rendering {template_path}: {e}")
            traceback.print_exc()


def render_all(trigger_file=None):
    env = Environment(loader=FileSystemLoader("templates"))
    data = load_data()
    render_all_templates(env, data, trigger_file)


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_event_time = 0
        self.last_event_path = None
        self.debounce_delay = 5  # seconds

    def should_process_event(self, event_path):
        current_time = time.time()
        if (self.last_event_path != event_path) or (current_time - self.last_event_time > self.debounce_delay):
            self.last_event_time = current_time
            self.last_event_path = event_path
            return True
        return False

    def on_modified(self, event):
        if self.should_process_event(event.src_path):
            rel_path = os.path.normpath(os.path.relpath(event.src_path))
            if rel_path.startswith(os.path.normpath("templates" + os.sep)) or rel_path.startswith(os.path.normpath("data" + os.sep)):
                render_all(event.src_path)

    def on_created(self, event):
        if self.should_process_event(event.src_path):
            rel_path = os.path.normpath(os.path.relpath(event.src_path))
            if rel_path.startswith(os.path.normpath("templates" + os.sep)) or rel_path.startswith(os.path.normpath("data" + os.sep)):
                render_all(event.src_path)

    def on_deleted(self, event):
        if self.should_process_event(event.src_path):
            rel_path = os.path.normpath(os.path.relpath(event.src_path))
            if rel_path.startswith(os.path.normpath("templates" + os.sep)) or rel_path.startswith(os.path.normpath("data" + os.sep)):
                render_all(event.src_path)


if __name__ == "__main__":
    render_all()

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, "templates/", recursive=True)
    observer.schedule(event_handler, "data/", recursive=True)
    observer.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
