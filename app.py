import pyodbc
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import SelectField
from wtforms.validators import DataRequired
from collections import defaultdict
import numpy as np
import time
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecureSecretKey'


def connection():
    server = 'txt6312server.database.windows.net'
    database = 'test'
    username = 'CloudSA3d95adf8'
    password = 'tiger@123TT'
    driver = '{ODBC Driver 18 for SQL Server}'
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    return conn


@app.route('/', methods=['GET', 'POST'])
def txt6312_main():
    try:
        conn = connection()
        cursor = conn.cursor()
        return render_template('index.html')
    except Exception as e:
        return render_template('index.html', error=e)


class txt6312_Show_By_Magnitude(FlaskForm):
    mag = StringField(label='Enter Magnitude: ', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


@app.route('/txt6312_Show_By_Magnitude', methods=['GET', 'POST'])
def txt6312_Show_By_Magnitude():
    try:
        conn = connection()
        cursor = conn.cursor()

        magnitude_ranges = [
            ("Mag. less than 1.0", "mag < 1"),
            ("Mag. between 1.0 to 2.0", "mag >= 1.0 AND mag < 2.0"),
            ("Mag. between 2.0 to 3.0", "mag >= 2.0 AND mag < 3.0"),
            ("Mag. between 3.0 to 4.0", "mag >= 3.0 AND mag < 4.0"),
            ("Mag. between 4.0 to 5.0", "mag >= 4.0 AND mag < 5.0"),
            ("Mag. greater than 5.0", "mag >= 5.0")
        ]

        result = {}
        cnt = 0

        start_time = time.time()

        counts = []
        for _, condition in magnitude_ranges:
            query = "SELECT COUNT(*) FROM earthquake WHERE " + condition
            cursor.execute(query)
            row = cursor.fetchone()
            count = row[0]
            counts.append(count)

        end_time = time.time()
        execution_time = end_time - start_time

        labels = [label for label, _ in magnitude_ranges]
        counts = np.array(counts)

        result = dict(zip(labels, counts))
        cnt = np.sum(counts)

        return render_template('txt6312_Show_By_Magnitude.html', result=result, cnt=cnt, data=1, execution_time=execution_time)

    except Exception as e:
        print(e)
        return render_template('txt6312_Show_By_Magnitude.html', error='Enter numeric value.')


class txt6312_Display_The_EQRecords_By_Mag_Depth_Ranges(FlaskForm):
    d1 = StringField(label='Lower Range of Depth: ', validators=[DataRequired()])
    d2 = StringField(label='Upper Range of Depth: ', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

@app.route('/txt6312_Display_The_EQRecords_By_Mag_Depth_Ranges', methods=['GET', 'POST'])
def txt6312_Display_The_EQRecords_By_Mag_Depth_Ranges_method():
    form = txt6312_Display_The_EQRecords_By_Mag_Depth_Ranges()
    if form.validate_on_submit():
        try:
            d1 = float(form.d1.data)
            d2 = float(form.d2.data)

            conn = connection()
            # cursor = conn.cursor()

            if d1 > d2:
                return render_template('txt6312_Display_The_EQRecords_By_Mag_Depth_Ranges.html', form=form, error='Lower range must be lower than upper range.')

            result = {}

            magnitude_ranges = [
                ("Mag. less than 1.0", "mag < 1.0"),
                ("Mag. between 1.0 to 2.0", "mag >= 1.0 AND mag < 2.0"),
                ("Mag. between 2.0 to 3.0", "mag >= 2.0 AND mag < 3.0"),
                ("Mag. between 3.0 to 4.0", "mag >= 3.0 AND mag < 4.0"),
                ("Mag. between 4.0 to 5.0", "mag >= 4.0 AND mag < 5.0"),
                ("Mag. greater than 5.0", "mag >= 5.0")
            ]

            query = "SELECT COUNT(*) as count FROM earthquake WHERE {} AND depth BETWEEN ? AND ?"

            for label, condition in magnitude_ranges:
                start_time = time.time()  # Start measuring execution time
                df = pd.read_sql_query(query.format(condition), conn, params=(d1, d2))
                end_time = time.time()  # Stop measuring execution time
                count = df['count'][0]
                result[label] = count

                execution_time = end_time - start_time  
            cnt = sum(result.values())

            return render_template('txt6312_Display_The_EQRecords_By_Mag_Depth_Ranges.html', result=result, form=form, cnt=cnt, d1=d1, d2=d2,execution_time=execution_time, data=1)

        except Exception as e:
            print(e)
            return render_template('txt6312_Display_The_EQRecords_By_Mag_Depth_Ranges.html', form=form, error='Enter numeric value.')

    return render_template('txt6312_Display_The_EQRecords_By_Mag_Depth_Ranges.html', form=form)

class txt6312_Graph_By_Records_Comp_Mag_VS_Depth(FlaskForm):
    m1 = StringField(label='Lower Range of Magnitude: ', validators=[DataRequired()])
    m2 = StringField(label='Upper Range of Magnitude: ', validators=[DataRequired()])
    d1 = StringField(label='Lower Range of Depth: ', validators=[DataRequired()])
    d2 = StringField(label='Upper Range of Depth: ', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

@app.route('/txt6312_Graph_By_Records_Comp_Mag_VS_Depth', methods=['GET', 'POST'])
def txt6312_Graph_By_Records_Comp_Mag_VS_Depth_method():

    form = txt6312_Graph_By_Records_Comp_Mag_VS_Depth()
    if form.validate_on_submit():
        try:
            conn = connection()
            m1 = float(form.m1.data)
            m2 = float(form.m2.data)
            d1 = float(form.d1.data)
            d2 = float(form.d2.data)

            if d1 > d2 or m1 > m2:
                return render_template('txt6312_Graph_By_Records_Comp_Mag_VS_Depth.html', form=form, error='Lower range must be lower than upper range.')

            query = "SELECT mag, depth FROM earthquake"
            cursor = conn.cursor()

            start_time = time.time()

            cursor.execute(query)
            rows = cursor.fetchall()
            data = np.array(rows)
            magnitudes = data[:, 0].astype(float)
            depths = data[:, 1].astype(float)

            mask = (m1 <= magnitudes) & (magnitudes <= m2) & (d1 <= depths) & (depths <= d2)
            result = data[mask]
            result_dict = {f"Record {i+1}": result[i].tolist() for i in range(len(result))}
            cnt = len(result_dict)

            elapsed_time = time.time() - start_time

            conn.close()

            return render_template('txt6312_Graph_By_Records_Comp_Mag_VS_Depth.html', result=result_dict, d1=d1, d2=d2, m1=m1, m2=m2, cnt=cnt, form=form, data=1, elapsed_time=elapsed_time)

        except Exception as e:
            print(e)
            return render_template('txt6312_Graph_By_Records_Comp_Mag_VS_Depth.html', form=form, error='Enter numeric value.')

    return render_template('txt6312_Graph_By_Records_Comp_Mag_VS_Depth.html', form=form)

class txt6312_Mag_Records_By_Categories(FlaskForm):
    type = SelectField('Select Category:', choices=[('earthquake', 'Earthquake'), ('ice quake', 'Ice Quake'),
                                                    ('explosion', 'Explosion'), ('quarry blast', 'Quarry Blast'),
                                                    ('other event', 'Other Event')], validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/txt6312_Mag_Records_By_Categories', methods=['GET', 'POST'])
def txt6312_Mag_Records_By_Categories_method():
    form = txt6312_Mag_Records_By_Categories()
    if form.validate_on_submit():
        try:
            conn = connection()
            cursor = conn.cursor()
            clus = form.type.data

            magnitude_ranges = [
                ("Mag. less than 1.0", "mag < 1"),
                ("Mag. between 1.0 to 2.0", "mag >= 1.0 AND mag < 2.0"),
                ("Mag. between 2.0 to 3.0", "mag >= 2.0 AND mag < 3.0"),
                ("Mag. between 3.0 to 4.0", "mag >= 3.0 AND mag < 4.0"),
                ("Mag. between 4.0 to 5.0", "mag >= 4.0 AND mag < 5.0"),
                ("Mag. greater than 5.0", "mag >= 5.0")
            ]

            result = {}
            cnt = 0
            start_time = time.time()


            for label, condition in magnitude_ranges:
                query = f"SELECT COUNT(*) FROM earthquake WHERE {condition} AND type = ?"
                cursor.execute(query, (clus,))
                row = cursor.fetchone()
                count = row[0]
                result[label] = count
                cnt += count

            elapsed_time = time.time() - start_time
            conn.close()

            return render_template('txt6312_Mag_Records_By_Categories.html', result=result, type=clus, cnt=cnt, form=form, data=1,elapsed_time=elapsed_time)

        except Exception as e:
            print(e)
            return render_template('txt6312_Mag_Records_By_Categories.html', form=form, error='Error occurred.')

    return render_template('txt6312_Mag_Records_By_Categories.html', form=form)

if __name__ == "__main__":
    app.run(debug=True, port=8080)