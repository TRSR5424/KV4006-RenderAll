# KV4006-RenderAll
Very basic static site generator, for KV4006 students at Northumbria University.

There are many very good static site generators. This isn't one of them. Please seriously consider your life choices if you're thinking of using this beyond KV4006.

## How to run

1. Clone the repository
2. Open the repository directory in PyCharm.
3. Populate the virtual environment.
4. Run the 'render-all.py' file.

## HELP MY IMAGES AREN'T LOADING
1. Open "render_all_lite" file
2. Go to line 101
3. If the file extenstion for your image isn't there add it to the list


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

On Windows, we need to target python 3.12, and build with mingw64

```
uv venv --python 3.12
uv run --python 3.12 python -m nuitka --onefile --mingw64 render_all_lite.py
```
