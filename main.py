from guizero import App, PushButton, TextBox, Box
from version import app_name, version, release_date

def render_all():
    """Start render watcher."""
    pass

def render_stop():
    """Stop render watcher."""
    pass

def exit_app():
    """Exit the application."""
    app.destroy()


if __name__ == "__main__":
    version_string = f">>> {app_name} v{version}, {release_date}"
    app = App(title=app_name, width=740, height=600, layout="auto")

    output_box = Box(app)
    output_message_box = TextBox(output_box, align="left", width=98, height=38, multiline=True, scrollbar=True, text=version_string)

    button_box = Box(app)
    button = PushButton(button_box, align="left", command=exit_app, text="Quit", width=20, height=3)
    button = PushButton(button_box, align="left", command=render_stop, text="Stop", width=20, height=3)
    button = PushButton(button_box, align="left", command=render_all, text="Go!", width=20, height=3)

    app.display()
