# KV4006-Render
 Very basic static site generator, for KV4006 students are Northumbria University

## How to run

1. Clone the repository
2. Open the repository directory in PyCharm.
3. Populate the virtual environment.
4. Run the 'render-all.py' file.


## Nuitka build

```
uv add --dev nuitka
uv run python -m nuitka --onefile render_all_lite.py
```

or

```
uv run python -m nuitka --standalone --macos-create-app-bundle render_all_lite.py
```

(actually better with the former, and using the .bin, I think.)
