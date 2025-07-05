
import os
from flask import Flask, request, render_template, send_file
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ZIP_PATH = 'renamed_files.zip'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        start_time = request.form['start_time']
        interval = int(request.form['interval'])
        exclude_times = [t.strip() for t in request.form['exclude_times'].split(',') if t.strip()]

        uploaded_files = request.files.getlist('folder')
        uploaded_files.sort(key=lambda f: f.stream._file.tell())

        current_time = datetime.strptime(f"{date} {start_time}", "%d.%m.%Y %H.%M")
        renamed_files = []

        # Clear previous uploads
        for f in os.listdir(UPLOAD_FOLDER):
            os.remove(os.path.join(UPLOAD_FOLDER, f))

        for file in uploaded_files:
            while current_time.strftime("%H.%M") in exclude_times:
                current_time += timedelta(minutes=interval)

            extension = os.path.splitext(file.filename)[1]
            new_name = f"{name} {date} &{current_time.strftime('%H.%M')}" + extension
            secure_new_name = new_name.replace("/","-").replace("\\","-").strip()
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_new_name)
            file.save(save_path)
            renamed_files.append(secure_new_name)

            current_time += timedelta(minutes=interval)

        # Create ZIP file
        with zipfile.ZipFile(ZIP_PATH, 'w') as zipf:
            for filename in renamed_files:
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                zipf.write(filepath, arcname=filename)

        return render_template('success.html', files=renamed_files)

    return render_template('index.html')

@app.route('/download')
def download_zip():
    return send_file(ZIP_PATH, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
