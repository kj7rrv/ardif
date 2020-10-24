from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import tempfile
import os
import subprocess
import more_itertools
import ardif
import datauri
import cv2

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'gif', 'png', 'bmp', 'tif', 'tiff']
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/image_to_ardif', methods=['POST'])
def image_to_ardif():
    if allowed_file(request.files['image'].filename):
        name = secure_filename(request.files['image'].filename)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, name)
            request.files['image'].save(path)
            if request.form['max_size'] and request.form['max_size'] != '0':
                command = [ 'convert', path, '-resize', str(int(request.form['max_size'])), path ]
                subprocess.call(command)
            color_divisors = {
                    '64': 1,
                    '32': 2,
                    '16': 4,
                    '8': 8,
                    '4': 16,
                    '2': 32,
                    }
            ardif_data = ardif.create_message(path, request.form['sender'], request.form['recipient'], request.form['title'], request.form['comment'], color_divisors[request.form['shades']])
            block_section = ''
            if request.form.get('block', '0') != '0':
                blocks = list(more_itertools.sliced(ardif_data, int(request.form['block'])))
                if len(blocks) > 1:
                    block_section = '<h2>Blocks</h2><div id=blocks>'
                    for block_id, block in enumerate(blocks):
                        block_section += render_template('block.html', number=block_id+1, data=block)
                    block_section += '</div>'
        return render_template('image_to_ardif.html',
                data_len=len(ardif_data),
                data=ardif_data
                ).replace('__block_section__', block_section)
        

@app.route('/ardif_to_image', methods=['POST'])
def ardif_to_image():
    portion_received = request.form.get('previous', '') + request.form['ardif']
    data = ardif.parse_message(portion_received)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'img.png')
        cv2.imwrite(path, data['image'])
        uri = datauri.DataURI.from_file(path)
    if not data['is_complete']:
        portion_received_escaped = portion_received.replace('\\', '\\\\').replace('"', '\\"')
        next_part = render_template('next_part_form.html', portion_received_escaped=portion_received_escaped)
    else:
        next_part = ''
    return render_template('ardif_to_image.html',
            sender=data['sender'],
            recipient=data['recipient'],
            date=data['date'],
            title=data['title'],
            comment=data['comment'],
            uri=uri,
            ).replace('__next_part__', next_part)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
