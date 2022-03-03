#THIS IS TEST-DEV1 REPO>change1>change2>change3>change4>change5

from os import access
from flask import Flask, render_template, request, redirect, url_for, session,abort
from flask_mysqldb import MySQL
import MySQLdb.cursors
from github import Github
import requests 
import jenkins
from flask_sqlalchemy import SQLAlchemy  
from sqlalchemy import or_,MetaData,create_engine,inspect
import credentials

g = Github(credentials.GITHUB_KEY)

# Intialize Flask
app = Flask(__name__)
# Intialize MySQL
mysql = MySQL(app)
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '%3&}QWkq+>y7<pqZ'

# Enter your database connection details below
app.config['MYSQL_HOST'] = credentials.MYSQL_HOST
app.config['MYSQL_USER'] = credentials.MYSQL_USER
app.config['MYSQL_PASSWORD'] = credentials.MYSQL_PASS
app.config['MYSQL_DB'] = credentials.MYSQL_DB

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+credentials.MYSQL_USER+':'+credentials.MYSQL_PASS+'@'+credentials.MYSQL_HOST+'/'+credentials.MYSQL_DB
db = SQLAlchemy(app)

class Flow_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(90))
    create_update_record = db.Column(db.String(90))
    field = db.Column(db.String(90))
    value =db.Column(db.String(90))
    trigger1 =db.Column(db.String(90))
    trigger2 =db.Column(db.String(90))
    trigger3 =db.Column(db.String(90))

class Table_access(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authentication_access_role = db.Column(db.String(45))
    authentication_edit_role = db.Column(db.String(45))
    host = db.Column(db.String(45))
    user = db.Column(db.String(45))
    password = db.Column(db.String(45))
    database = db.Column(db.String(45))
    table=db.Column(db.String(45))


# Enter your Jenkins Server connection details bellow
server = jenkins.Jenkins(credentials.JENKINS_HOST,credentials.JENKINS_USER, credentials.JENKINS_PASS)


@app.route('/login', methods=['GET', 'POST'])
def login():
    #Developer 0
    #Admin 3

    # Output message if something goes wrong...
    msg = ''
    # Check if "email" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        # Check if account exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        account = cursor.fetchone()

        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['role'] = account['role']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect email/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
# Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   session.pop('role', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if session['role'] == 3 :
            cursor.execute('SELECT * FROM auto_project_update order by developer_id')
        else :
            cursor.execute('SELECT * FROM auto_project_update where developer_id = "'+session["email"]+'";')
        projects = cursor.fetchall()
        return render_template('home.html', email=session['email'],projects=projects)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/databases',methods=['GET'])
def databases():
    if 'loggedin' in session:
        accesses = db.session.query(Table_access.database).distinct()
        return render_template("databases.html",accesses=accesses)
    return redirect(url_for('login'))

@app.route('/get_tables',methods=['POST'])
def getTables():
    if 'loggedin' in session:
        data = Table_access.query.filter_by(database=request.form["database"]).first()
        engine = create_engine('mysql://'+data.user+':'+data.password+'@'+data.host+'/'+data.database)
        inspector = inspect(engine)
        return {"tables":inspector.get_table_names()}
    return redirect(url_for('login'))

@app.route('/table/<database>/<table>',methods=['GET', 'POST'])
def table(database,table):
    if 'loggedin' in session:
        data = Table_access.query.filter_by(database=database,table=table).first()
        if(not data):
            data = Table_access.query.filter_by(database=database).first()
        if(session["role"]<int(data.authentication_access_role or (not data))):
            return "Sorry You are not Allowed to access"
        else:
            engine = create_engine('mysql://'+data.user+':'+data.password+'@'+data.host+'/'+data.database)
            if(request.method=='GET'): 
                rows = engine.execute('SELECT * FROM '+table)
                inspector = inspect(engine)
                return render_template('table.html', rows=list(rows.fetchall()),tables=inspector.get_table_names(),table=table,keys=list(rows.keys()),database=database)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/table/create/<database>/<table>',methods=['POST'])
def tableCreate(database,table):
    
    if 'loggedin' in session:
        data = Table_access.query.filter_by(database=database,table=table).first()
        if(not data):
            data = Table_access.query.filter_by(database=database).first()

        if(session["role"]<int(data.authentication_edit_role)):
            return "Sorry You are not Allowed to edit"
        else:
            engine = create_engine('mysql://'+data.user+':'+data.password+'@'+data.host+'/'+data.database)
            values = " VALUES ("
            columns = " ("
            rows = engine.execute('SELECT * FROM '+table)
            for key in list(rows.keys())[1:]:
                values+="'"+request.form[key]+"',"
                columns+=key+","
            values=values[:-1]+")"
            columns=columns[:-1]+") "

            engine.execute("INSERT INTO "+table+columns+values)
            try:
                script_name1 = Flow_table.query.filter_by(table_name=table,create_update_record="create").first().trigger1
                script_name2 = Flow_table.query.filter_by(table_name=table,create_update_record="create").first().trigger2
                script_name3 = Flow_table.query.filter_by(table_name=table,create_update_record="create").first().trigger3
            
                try:
                    if(script_name1):
                        exec(open('static/python_scripts/'+script_name1).read())
                    if(script_name2):
                        exec(open('static/python_scripts/'+script_name2).read())
                    if(script_name3):
                        exec(open('static/python_scripts/'+script_name3).read())
                except:
                    abort(404)
            except:
                pass
            return redirect("/table"+"/"+database+"/"+table)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/table/delete/<database>/<table>',methods=['POST'])
def tableDelete(database,table):
    if 'loggedin' in session:
        data = Table_access.query.filter_by(database=database,table=table).first()
        if(not data):
            data = Table_access.query.filter_by(database=database).first()
        if(session["role"]<int(data.authentication_edit_role)):
            abort(401)
        else:
            engine = create_engine('mysql://'+data.user+':'+data.password+'@'+data.host+'/'+data.database)
            todelete = engine.execute("select * FROM "+table+" where id="+"'"+request.form["id"]+"'").first()
            engine.execute("DELETE FROM "+table+" where id="+"'"+request.form["id"]+"'")
            try:
                script_name1 = Flow_table.query.filter_by(table_name=table,create_update_record="delete").first().trigger1
                script_name2 = Flow_table.query.filter_by(table_name=table,create_update_record="delete").first().trigger2
                script_name3 = Flow_table.query.filter_by(table_name=table,create_update_record="delete").first().trigger3
            
                try:
                    if(script_name1):
                        exec(open('static/python_scripts/'+script_name1).read())
                    if(script_name2):
                        exec(open('static/python_scripts/'+script_name2).read())
                    if(script_name3):
                        exec(open('static/python_scripts/'+script_name3).read())
                except:
                    abort(404)
            except:
                pass
            return "200"
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/table/update/<database>/<table>/<id>',methods=['POST','GET'])
def tableUpdate(database,table,id):
    
    if 'loggedin' in session:
        data = Table_access.query.filter_by(database=database,table=table).first()
        if(not data):
            data = Table_access.query.filter_by(database=database).first()

        if(session["role"]<int(data.authentication_edit_role)):
            return "Sorry You are not Allowed to edit"
        else:
            engine = create_engine('mysql://'+data.user+':'+data.password+'@'+data.host+'/'+data.database)
            if request.method == 'GET':
                rows = engine.execute('SELECT * FROM '+table+" where id="+id)
                return render_template('update.html', row=list(rows.fetchall())[0],table=table,keys=list(rows.keys()),database=database,id=id)
            elif request.method == 'POST':
                values = ""
                rows = engine.execute('SELECT * FROM '+table)
                for key in list(rows.keys())[1:]:
                    values+= key+"="+"'"+request.form[key]+"',"

                engine.execute('update '+table+" set "+ values[:-1]+" where id="+id)
                try:
                    up = Flow_table.query.filter_by(table_name=table,create_update_record="update").first()
                    script_name1 = up.trigger1
                    script_name2 = up.trigger2
                    script_name3 = up.trigger3
                    if(request.form[up.field]==up.value):
                        try:
                            if(script_name1):
                                exec(open('static/python_scripts/'+script_name1).read())
                            if(script_name2):
                                exec(open('static/python_scripts/'+script_name2).read())
                            if(script_name3):
                                exec(open('static/python_scripts/'+script_name3).read())
                        except:
                            abort(404)
                except:
                    pass

                return redirect("/table"+"/"+database+"/"+table)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/project/git-log',methods=['POST'])
def gitLog():
    if 'loggedin' in session:
        try:
            repo = g.get_repo(request.form["main_project_id"])
            pr = repo.get_pull(int(request.form["merge_id"]))
        except Exception as e:
            abort(e.status)
        return pr.mergeable_state
    return redirect(url_for('login'))


@app.route('/project/jenkins-log',methods=['POST'])
def jenkinsLog():
    if 'loggedin' in session:
        logs=""
        try:
            logs = server.get_job_info(request.form["project_name"])
        except Exception as e:
            abort(404)
        return logs
    return redirect(url_for('login'))


@app.route('/project/jenkins-log-number',methods=['POST'])
def jenkinsLogNumber():
    if 'loggedin' in session:
        logs=""
        try:
            logs = server.get_build_console_output(request.form["project_name"],int(request.form["build_number"]))
        except Exception as e:
            abort(404)
        return logs
    return redirect(url_for('login'))

@app.route('/project/grafana-log',methods=['POST'])
def grafanaLog():
    if 'loggedin' in session:
        logs=""
        try:
            app_inf = request.form["log_path_pod"].split(',')
            data = requests.get("http://"+credentials.GRAFANA_USER+":"+credentials.GRAFANA_PASS+"@"+credentials.GRAFANA_HOST+"/api/datasources/proxy/2/loki/api/v1/query_range?direction=BACKWARD&limit=2000&query=%7Bnamespace%3D%22"+app_inf[0]+"%22%2Capp%3D%22"+app_inf[1]+"%22%7D").json()
            logs = {"logs":data["data"]["result"][0]["values"]}
        except Exception as e:
            abort(e.status)
        return logs
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0")
