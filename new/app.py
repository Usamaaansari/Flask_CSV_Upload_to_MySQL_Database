from flask import Flask,render_template,request
from sqlalchemy import create_engine
from sqlalchemy import text
import os
import shutil
import pandas as pd

app=Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

sql = "mysql://root:root@localhost:3306/publisher"
engine=create_engine(sql)
conn=engine.connect()
conn.execute(text('create table if not exists elsevier(Title varchar(2000),Authors varchar(2000),DOI varchar(500),Abstract varchar(5000),Email varchar(200), Affiliations varchar(2000))'))
conn.close()

# Check if the upload folder exists, if not, create it
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template("csv.html")

@app.route('/csv',methods=["GET","POST"])
def csv():
    if 'files[]' not in request.files:
        return 'No file part'
    files = request.files.getlist('files[]')
    for file in files:
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
        # Create a DataFrame
    for filename in os.listdir('./uploads'):
        if filename.endswith(".csv"):
                filepath = os.path.join('./uploads', filename)
                df=pd.read_csv(filepath,encoding='utf-8')
                sql = "mysql://root:root@localhost:3306/publisher"
                engine=create_engine(sql)
                conn=engine.connect()
                df.to_sql('elsevier', conn, index=False, if_exists='append')
                
                conn.close()
                shutil.move(filepath, './Elsevier')

    return render_template("back.html")

@app.route('/data')
def data():
    sql = "mysql://root:root@localhost:3306/publisher"
    engine=create_engine(sql)
    conn=engine.connect()
    results=conn.execute(text('select * from elsevier'))
    df=pd.DataFrame(results)
    colnames = conn.execute(text('desc elsevier'))
    columns=[]
    for row in colnames:
        columns.append(row[0])
    conn.close()
    return render_template("data.html",length=len(df), columns=columns,data=df.to_html())

if __name__=='__main__':
    app.run()