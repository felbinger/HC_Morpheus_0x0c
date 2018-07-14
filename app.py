#!/usr/bin/env python

from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.debug import DebuggedApplication
import re
import os
import xml.sax


class Config(object):
    UPLOAD_FOLDER = '.'


ALLOWED_EXTENSIONS = set(['xml'])
app = Flask(__name__)
app.config.from_object(Config)
app.debug = True


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class VideoParse(xml.sax.handler.ContentHandler):
    def __init__(self, object):
        self.obj = object
        self.curpath = []

    def startElement(self, name, attrs):
        self.chars = ""
        print
        name, attrs

    def endElement(self, name):
        if name in set(['title', 'url', 'description']):
            self.obj[name] = self.chars

    def characters(self, content):
        self.chars += content


def process_xml(filename, path):
    parser = xml.sax.make_parser()
    object = {}
    handler = VideoParse(object)
    parser.setContentHandler(handler)
    parser.parse(open(filename))
    return " Upload was successful: \r\n " + \
           " Title: " + object["title"] + "\r\n" + \
           " URL: " + object["url"] + "\r\n" + \
           " Description: " + object["description"] + "\r\n" + \
           " announcement saved: " + url_for('uploaded_file', filename=filename)


@app.route('/', methods=['GET'])
def index():
    return '''
    <h1>Video Announcements</h1>
    <!-- Todo: create the video announcements dynamically -->
    <table border=1 style="width:100%">
      <tr>
        <th>Title</th>
        <th>URL</th>
        <th>Description</th>
      </tr>
      <tr>
      <td>Lern programming - XML and JSON</td>
      <td><a href="https://www.youtube.com/watch?v=GRKkyF6Bkok"></a></td>
      <td>Awesome!</td>
      </tr>
    </table>
    '''


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            return process_xml(filename, os.path.abspath(Config.UPLOAD_FOLDER))
    return '''
    <title>Create new announcement</title>
    <h1>Announce a new video</h1>
    <p>Attributes are title, url and description</p>
    <!-- TODO: make XML schema to verify the uploaded data -->
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888)
