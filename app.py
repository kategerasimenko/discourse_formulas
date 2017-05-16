from flask import Flask, request, render_template, send_file
from for_app import get_all
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'txt'


@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        speakers = True if 'speakers' in request.form else False
        if file.filename == '':
            return 'Не выбран файл!'
        if file and allowed_file(file.filename):
            fname = file.filename
            file = file.read()
            try:
                text = file.decode("utf-8")
            except:
                text = file.decode("cp1251")
            results = get_all(text,fname,speakers)
            return send_file('formula_list.csv',as_attachment=True)
        return 'Неверный формат файла! Необходимо загрузить txt-файл.'
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
        
