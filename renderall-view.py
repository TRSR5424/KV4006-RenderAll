from flask import Flask, render_template, request, jsonify
import os
import re
from pygments import highlight
from pygments.lexers import HtmlLexer
from pygments.lexers.templates import DjangoLexer
from pygments.formatters import HtmlFormatter
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Text, Comment, Operator, Keyword, Name, String, Number, Punctuation

app = Flask(__name__, template_folder='view-templates')

TEMPLATES_DIR = 'templates'

class HtmlJinjaLexer(RegexLexer):
    name = 'HTML+Jinja'
    aliases = ['html+jinja']
    filenames = ['*.html', '*.htm']

    tokens = {
        'root': [
            (r'(\{%)(-?\s*end\w+\s*-?)(%\})',
             bygroups(Comment.Preproc, Comment.Preproc, Comment.Preproc)),
            (r'(\{%)(-?\s*\w+\s*-?)(%\})',
             bygroups(Comment.Preproc, Comment.Preproc, Comment.Preproc)),
            (r'(\{\{)(-?\s*.*?\s*-?)(\}\})',
             bygroups(Comment.Preproc, Comment.Preproc, Comment.Preproc)),
            (r'(\{#)(.*?)(#\})',
             bygroups(Comment.Preproc, Comment.Preproc, Comment.Preproc)),
            include('html'),
        ],
        'html': [
            (r'<!--', Comment, 'comment'),
            (r'<!\[CDATA\[', Comment.Preproc, 'cdata'),
            (r'<!DOCTYPE.*?>', Comment.Preproc),
            (r'<\?.*?\?>', Comment.Preproc),
            (r'(<)([\w:.-]+)', bygroups(Punctuation, Name.Tag), 'tag'),
            (r'[^<&]+', Text),
            (r'&\S*?;', Name.Entity),
            (r'<', Text),
        ],
        'comment': [
            (r'[^-]+', Comment),
            (r'-->', Comment, '#pop'),
            (r'-', Comment),
        ],
        'cdata': [
            (r'[^\]]+', Comment.Preproc),
            (r'\]\]>', Comment.Preproc, '#pop'),
            (r'\]', Comment.Preproc),
        ],
        'tag': [
            (r'\s+', Text),
            (r'([\w:-]+\s*)(=)(\s*)', bygroups(Name.Attribute, Operator, Text), 'attr'),
            (r'[\w:-]+', Name.Attribute),
            (r'/?\s*>', Punctuation, '#pop'),
        ],
        'attr': [
            (r'\s+', Text),
            (r'"[^"]*"', String, '#pop'),
            (r"'[^']*'", String, '#pop'),
            (r'[^\s>]+', String, '#pop'),
        ],
    }

def get_file_list(directory):
    file_tree = {}
    for root, dirs, files in os.walk(directory):
        rel_root = os.path.relpath(root, directory)
        if rel_root == '.':
            rel_root = ''
        file_tree[rel_root] = [f for f in files if f != '.DS_Store']
    return file_tree

def read_file(file_path):
    print(f">>> READING FILE: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def analyze_template(file_content):
    extends_match = re.search(r'{%\s*extends\s+[\'"](.+?)[\'"]\s*%}', file_content)
    includes = re.findall(r'{%\s*include\s+[\'"].+?[\'"]\s*%}', file_content)
    macros = re.findall(r'{%\s*macro\s+\w+\s*\(.*?\)\s*%}', file_content)
    return {
        'extends': extends_match.group(1) if extends_match else None,
        'includes': len(includes),
        'macros': len(macros)
    }

@app.route('/')
def index():
    files = get_file_list(TEMPLATES_DIR)
    file_info = {}
    for dir, file_list in files.items():
        file_info[dir] = []
        for file in file_list:
            full_path = os.path.join(TEMPLATES_DIR, dir, file)
            file_content = read_file(full_path)
            analysis = analyze_template(file_content)
            file_info[dir].append({
                'name': file,
                'extends': analysis['extends'],
                'includes': analysis['includes'],
                'macros': analysis['macros']
            })
    return render_template('index.html', files=file_info)

@app.route('/view')
def view_file():
    file_path = request.args.get('file')
    if not file_path:
        return "No file specified", 400

    full_path = os.path.join(TEMPLATES_DIR, file_path)
    if not os.path.exists(full_path):
        return "File not found", 404

    file_content = read_file(full_path)
    lexer = HtmlJinjaLexer(stripall=True)
    formatter = HtmlFormatter(linenos=True, cssclass="source")
    highlighted_code = highlight(file_content, lexer, formatter)

    return jsonify({'file': file_path, 'code': highlighted_code, 'css': formatter.get_style_defs('.source')})

if __name__ == '__main__':
    app.run(debug=True)
