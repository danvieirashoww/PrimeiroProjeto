import os
from uuid import uuid4

from flask import Flask, render_template, request, send_from_directory
from rembg import remove

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'input')
app.config['OUTPUT_FOLDER'] = os.path.join('static', 'output')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image = request.files.get('image')
        if image and image.filename:
            ext = os.path.splitext(image.filename)[1].lower() or '.png'
            input_name = f"{uuid4().hex}{ext}"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_name)
            image.save(input_path)

            output_name = f"{uuid4().hex}.png"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)
            with open(input_path, 'rb') as inp:
                result = remove(inp.read())
            with open(output_path, 'wb') as out:
                out.write(result)

            return render_template('index.html', filename=output_name)
    return render_template('index.html', filename=None)


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
