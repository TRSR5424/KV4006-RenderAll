from livereload import Server

from render_all_lite import render_all

if __name__ == "__main__":
    render_all()

    server = Server()

    # The *args bit here avoids some nasty errors when the watch triggers
    # on a directory create/delete event.
    # The isinstance(path, list) parts check if the path is a list of paths,
    # which can happen when a directory is created or deleted. If so, they pass
    # only the first path to render_all, again to avoid an error.
    server.watch("templates/**/*.j2", lambda path, *args: render_all(path[0] if isinstance(path, list) else path))
    server.watch("templates/**/*.jinja", lambda path, *args: render_all(path[0] if isinstance(path, list) else path))
    server.watch("templates/**/*.html", lambda path, *args: render_all(path[0] if isinstance(path, list) else path))
    server.watch("data/*.json", lambda path, *args: render_all(path[0] if isinstance(path, list) else path))
    server.watch("data/*.[yY][aA][mM][lL]", lambda path, *args: render_all(path[0] if isinstance(path, list) else path))
    server.serve(root="site")
