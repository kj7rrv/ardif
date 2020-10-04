from flask import Flask, request
from werkzeug.utils import secure_filename
import tempfile
import os
import subprocess
app = Flask(__name__)
import ardif
import datauri
import cv2

@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html>
    <head>
        <title>ARDIF</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
#imagetoardif label {
    width: 7em;
    display: inline-block;
}
#image label {
    width: 12em;
}
select {
    margin: 0px;
    padding: 0px;
}
form, form * {
    background-color: #444444;
}
input {
    background-color: #555555;
    border: none;
    margin: 2px;
}
button {
    background-color: #555555;
    border: none;
    margin: 5px;
    box-shadow: 0px 0px 5px black;
}
button:hover {
    box-shadow: 0px 0px 3px black;
}
* {
    font-family: monospace;
    color: white;
    background-color: #222222;
}
        </style>
    </head>
    <body>
        <h1>ARDIF Converter</h1>
        <section id=imagetoardif>
            <h2>Image to ARDIF</h2>
            <form method=POST action="/image_to_ardif" enctype="multipart/form-data">
                <fieldset id=callsigns>
                    <legend>Callsigns</legend>
                    <label for=sender>Sender: </label><input type=text name=sender id=sender><br>
                    <label for=recipient>Recipient: </label><input type=text name=recipient id=recipient><br>
                </fieldset>
                <fieldset id=info>
                    <legend>Information</legend>
                    <label for=title>Title: </label><input type=text name=title id=title><br>
                    <label for=comment>Comment: </label><input type=text name=comment id=comment><br>
                </fieldset>
                <fieldset id=image>
                    <legend>Image</legend>
                    <label for=image>File: </label><input type=file name=image id=image><br>
                    <label for=max_size>Maximum dimension: </label><input type=number value=0 name=max_size id=max_size><br>
                    <label for=shades>Shades of gray: </label>
                    <select name=shades id=shades>
                        <option value=64>64</option>
                        <option value=32>32</option>
                        <option value=16>16</option>
                        <option value=8>8</option>
                        <option value=4>4</option>
                        <option value=2>B&W</option>
                    </select>
                </fieldset>
                <button>Convert</button>
            </form>
        </section>
        <section>
            <h2>ARDIF to Image</h2>
            <form method=POST action="/ardif_to_image">
                <label for=ardif>ARDIF: </label><input type=text id=ardif name=ardif><br>
                <button>Convert</button>
            </form>
        </section>
        <script>
            sender = document.querySelector('#sender')
            sender.value = localStorage.getItem('mycallsign') || ''
            sender.addEventListener('change', function() {
                localStorage.setItem('mycallsign', sender.value)
            })
        </script>
    </body>
</html>'''

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
        
        return f'''<!DOCTYPE html>
<html>
    <head>
        <title>ARDIF</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
* {{
    font-family: sans-serif;
    color: white;
    background-color: #222222;
    font-family: monospace;
}}
button {{
    background-color: #444444;
    border: none;
    margin: 5px;
    box-shadow: 0px 0px 5px black;
}}
button:hover {{
    box-shadow: 0px 0px 3px black;
}}
        </style>
    </head>
    <body>
        <h1>ARDIF Converter</h1>
        <p>Length {len(ardif_data)} bytes.</p>
        <input type=text id=data value="{ardif_data}">
        <button id=copy style='display: none'>Copy to clipboard</button><br>
        <a href=/>Home</a>
        <script>
button = document.querySelector('#copy')
input = document.querySelector('#data')
button.style = ''
input.style = 'display: none'
button.addEventListener('click', function(e) {{
    e.preventDefault()
    input.style = ''
    input.select()
    input.setSelectionRange(0, 9999999999999999)
    document.execCommand("copy")
    input.style = 'display: none'
    }}
)
        </script>
    </body>
</html>'''

@app.route('/ardif_to_image', methods=['POST'])
def ardif_to_image():
        with tempfile.TemporaryDirectory() as tmp:
            data = ardif.parse_message(request.form['ardif'])
            path = os.path.join(tmp, 'img.png')
            cv2.imwrite(path, data['image'])
            uri = datauri.DataURI.from_file(path)
        return f'''<!DOCTYPE html>
<html>
    <head>
        <title>ARDIF</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
table {{
    border-collapse: collapse;
    background-color: #444444;
}}
th, td {{
    margin-right: 0px;
    margin-left: 0px;
    padding: 3px;
}}
th {{
    border-right: 2px solid white;
    text-align: right;
}}
img {{
    display: block;
    padding: 3px;
}}
* {{
    font-family: sans-serif;
    color: white;
    background-color: #222222;
    font-family: monospace;
}}
        </style>
    </head>
    <body>
        <h1>ARDIF Converter</h1>
        <table>
            <tr><th>Sender</th><td>{data['sender']}</td></tr>
            <tr><th>Recipient</th><td>{data['recipient']}</td></tr>
            <tr><th>Date</th><td>{data['date']} UTC</td></tr>
            <tr><th>Title</th><td>{data['title']}</td></tr>
            <tr><th>Comment</th><td>{data['comment']}</td></tr>
        </table>
        <img src="{uri}"><br>
        <a href=/>Home</a>
    </body>
</html>'''
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
