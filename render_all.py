from livereload import Server

from render_all_lite import render_all

if __name__ == "__main__":
    render_all()

    server = Server()

    # The *args bit here avoids some nasty errors when the watch triggers
    # on a directory create/delete event.
    server.watch("templates/**/*.j2", lambda path, *args: render_all(path))
    server.watch("templates/**/*.jinja", lambda path, *args: render_all(path))
    server.watch("templates/**/*.html", lambda path, *args: render_all(path))
    server.watch("data/*.json", lambda path, *args: render_all(path))
    server.watch("data/*.[yY][aA][mM][lL]", lambda path, *args: render_all(path))
    server.serve(root="site")
