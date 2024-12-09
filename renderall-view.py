from flask import Flask, render_template, request, jsonify
import os
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

app = Flask(__name__, template_folder='view-templates')

TEMPLATES_DIR = 'templates'

def get_file_list(directory):
    file_tree = {}
    for root, dirs, files in os.walk(directory):
        rel_root = os.path.relpath(root, directory)
        if rel_root == '.':
            rel_root = ''
        file_tree[rel_root] = files
    return file_tree

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

@app.route('/')
def index():
    files = get_file_list(TEMPLATES_DIR)
    return render_template('index.html', files=files)

@app.route('/view')
def view_file():
    file_path = request.args.get('file')
    if not file_path:
        return "No file specified", 400

    full_path = os.path.join(TEMPLATES_DIR, file_path)
    if not os.path.exists(full_path):
        return "File not found", 404

    file_content = read_file(full_path)
    lexer = get_lexer_by_name('html', stripall=True)
    formatter = HtmlFormatter(linenos=True, cssclass="source")
    highlighted_code = highlight(file_content, lexer, formatter)

    return jsonify({'file': file_path, 'code': highlighted_code, 'css': formatter.get_style_defs('.source')})

if __name__ == '__main__':
    app.run(debug=True)
