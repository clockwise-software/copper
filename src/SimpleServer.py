# CLOCKWISE-BOOTCAMP SimpleServer.py
# Based on Server from Dr. Ian Cooper @ Cardiff
# Updated by Dr. Mike Borowczak @ UWyo March 2021

import os
from flask import Flask, redirect, request, render_template, jsonify
import sqlite3

DATABASE = 'bootcamp.db'

app = Flask(__name__)


@app.route("/")
def basic():
    return render_template('Employee.html')


@app.route("/Employee/AddEmployee", methods=['POST', 'GET'])
def studentAddDetails():
    if request.method == 'GET':
        return render_template('EmployeeData.html')
    if request.method == 'POST':
        firstName = request.form.get('firstName', default="Error")
        lastName = request.form.get('lastName', default="Error")
        businessunit = request.form.get('bu', default="Error")
        state = request.form.get('state', default="Error")
        print("inserting employee"+firstName)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO EmployeeList ('FirstName', 'LastName', 'Business Unit', 'State/Province')\
                        VALUES (?,?,?,?)", (firstName, lastName, businessunit, state))

            conn.commit()
            msg = "Record successfully added"
        except:
            conn.rollback()
            msg = "error in insert operation"
        finally:
            conn.close()
            return msg


@app.route("/Employee/Search", methods=['GET', 'POST'])
def surnameSearch():
    if request.method == 'GET':
        return render_template('EmployeeSearch.html')
    if request.method == 'POST':
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()

            # Build the SQL query dynamically based on what input values are provided
            sql_string_prefix = "SELECT * FROM EmployeeList WHERE "
            where_sub_filters = []

            # Extend the possible filterable entry types by adding the this list
            for filter_str in ["City", "State/Province", "Skill", "Registered Licenses"]:
                form_data = request.form.get(filter_str, default="")

                # Only add the section of the string to the query if it isn't empty
                if (form_data != ""):
                    sql_string_prefix += "\"" + filter_str + "\"" + " LIKE ? AND "
                    where_sub_filters.append(form_data + "%")

            # Remove trailing "AND" and postfix semicolon to close query.
            # Add further options before the ; and after the slice
            sql_string_prefix = sql_string_prefix[:-4] + ";"

            cur.execute(sql_string_prefix, tuple(where_sub_filters))
            data = cur.fetchall()
        except:
            print("Something went wrong with the /Employee/Search Endpoint")
            conn.close()
        finally:
            conn.close()
            # return str(data)
            return render_template('Employee.html', data=data)


# invoke this GET endpoint to receive a list of all the relevant searches so far
@app.route("/Search/Autocomplete/Lastname", methods=['GET'])
def lastname_autocomplete():
    if request.method == 'GET':
        try:
            search_name_start = request.args.get('LastName', default="")
            search_name_start += "%"

            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM EmployeeList WHERE LastName LIKE ? ;", (search_name_start))
            data = cur.fetchall()
        except:
            print('lastnameAutocomplete encountered an error.', data)
            conn.close()
        finally:
            conn.close()
            return jsonify(data)
    else:
        print('Error in lastnameAutocomplete: Invalid request method.')


if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
