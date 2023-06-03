from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from neo4j import GraphDatabase, basic_auth
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-most-secret-key'

# Neo4j credentials .. this is just for testing, please do not put credentials in plain text for production
neo4j_uri = 'bolt://<YOUR_NEO4J_DATABASE_ADDRESS>:7687'
neo4j_user = 'neo4j'
neo4j_password = 'your-neo4j-password'

# CSV file path
csv_file_path = 'data.csv'

# Neo4j driver
driver = GraphDatabase.driver(neo4j_uri, auth=basic_auth(neo4j_user, neo4j_password))


# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Sample user (replace with your own authentication method)
USER = {
    'username': 'admin',
    'password': 'your-very-strong-apps-password-here'
}

# Login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Form for csv addition
class UploadForm(FlaskForm):
    entity = StringField('Entity', validators=[DataRequired()])


# Form for manual node addition
class NodeForm(FlaskForm):
    label = StringField('Label', validators=[DataRequired()])
    node_name = StringField('Node Name', validators=[DataRequired()])
    submit_node = SubmitField('Add Node')

# Form for manual relationship addition
class RelationshipForm(FlaskForm):
    source_node_label = StringField('Source Node Label', validators=[DataRequired()])
    source_node = StringField('Source Node', validators=[DataRequired()])
    target_node_label = StringField('Target Node Label', validators=[DataRequired()])
    target_node = StringField('Target Node', validators=[DataRequired()])
    relationship_type = StringField('Relationship Type', validators=[DataRequired()])
    submit_relationship = SubmitField('Add Relationship')

# Home page
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    node_form = NodeForm()
    relationship_form = RelationshipForm()
    upload_form = UploadForm()

    if request.method == 'POST':
        if 'csv_file' in request.files:
            csv_file = request.files['csv_file']
            if csv_file.filename != '':
                csv_file.save(csv_file_path)
                if upload_form.entity.data == 'Education':
                    insert_education_from_csv()
                    flash('Education data inserted successfully from csv file!')
                if upload_form.entity.data == 'Transaction':
                    insert_transaction_from_csv()
                    flash('Transaction data inserted successfully from csv file!')
                if upload_form.entity.data == 'Trips':
                    insert_trips_from_csv()
                    flash('Trips data inserted successfully from csv file!')
                if upload_form.entity.data == 'Work':
                    insert_work_from_csv()
                    flash('Work data inserted successfully from csv file!')

        if node_form.validate_on_submit():
            insert_node(
                node_form.label.data, 
                node_form.node_name.data
            )
            flash('Node added successfully!')

        if relationship_form.validate_on_submit():
            insert_relationship(
                relationship_form.source_node_label.data,
                relationship_form.source_node.data,
                relationship_form.target_node_label.data,
                relationship_form.target_node.data,
                relationship_form.relationship_type.data
            )
            flash('Relationship added successfully!')
        

    return render_template('index.html', upload_form=upload_form,node_form=node_form, relationship_form=relationship_form)


# Insert education data from csv to Neo4j
def insert_education_from_csv():
    with driver.session() as session:
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row

            for row in csv_reader:
                query = '''
                MERGE (p:Person {passportNumber:'%s', name: '%s'})
                MERGE (c:Country {name: '%s'})
                MERGE (r:Course {name: '%s'})
                MERGE (i:Institution {name: '%s'})
                MERGE (p)-[x:TOOK_COURSE]->(r)
                SET x.startYear=%s
                SET x.endYear=%s
                MERGE (p)-[y:STUDIED_AT]->(i)
                SET y.startYear=%s
                SET y.endYear=%s
                MERGE (r)-[:ENROLLED_BY]->(i)
                MERGE (i)-[:LOCATED_IN]->(c)
                ''' % (row[0],row[1],row[2],row[4],row[3],row[5],row[6],row[5],row[6])
                session.run(query)

# Insert transaction data from csv to Neo4j
def insert_transaction_from_csv():
    with driver.session() as session:
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row

            for row in csv_reader:
                query = '''
                MERGE (c:Card {name: '%s'})
                MERGE (m:Merchant {name: '%s'})
                MERGE (co:Country {name: '%s'})
                MERGE (c)-[y:TRANSACT_AT]->(m)
                SET y.transactionDate='%s'
                SET y.amount=%s
                MERGE (m)-[:TRANSACTION_COUNTRY]->(co)
                ''' % (row[3],row[5],row[2],row[4],float(row[6].replace('$','')))
                session.run(query)

                query2 = '''
                MATCH (p:Person),(c:Card) WHERE p.passportNumber = '%s' AND c.name = '%s'
                MERGE (p)-[x:USING_CARD]->(c)
                '''% (row[0],row[3])
                session.run(query2)

# Insert trips data from csv to Neo4j
def insert_trips_from_csv():
    with driver.session() as session:
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row

            for row in csv_reader:
                query = '''
                MERGE (dc:Country {name: '%s'})
                MERGE (ac:Country {name: '%s'})      
                WITH dc,ac
                MATCH (p:Person),(dc:Country),(ac:Country) WHERE p.passportNumber = '%s' 
                SET p.citizenship='%s'
                MERGE (p)-[x:TRAVEL_FROM]->(dc)
                SET x.departureDate='%s'
                MERGE (p)-[y:TRAVEL_TO]->(ac)
                SET y.arrivalDate='%s'        
                ''' % (row[4],row[6],row[0],row[2],row[3],row[5])
                session.run(query)

# Insert work data from csv to Neo4j
def insert_work_from_csv():
    with driver.session() as session:
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row

            for row in csv_reader:
                query = '''
                MERGE (c:Country {name: '%s'})
                MERGE (org:Company {name: '%s'})
                MERGE (ro:Role {name: '%s'})         
                WITH c,org,ro
                MATCH (p:Person) WHERE p.passportNumber = '%s' 
                MERGE (p)-[x:HAS_ROLE]->(ro)
                SET x.startYear='%s'
                SET x.endYear='%s'
                MERGE (ro)-[y:WORK_AT]->(org)
                MERGE (org)-[z:COMPANY_LOCATED_IN]->(c)
                ''' % (row[2],row[3],row[4],row[0],row[5],row[6])
                session.run(query)


# Insert a single node into Neo4j
def insert_node(label, node_name):
    with driver.session() as session:
        query = '''
        MERGE (n:%s {name:'%s'})
        ''' % (label,node_name)
        session.run(query)

# Insert a relationship between two nodes in Neo4j
def insert_relationship(source_node_label,source_node,target_node_label, target_node, relationship_type):
    with driver.session() as session:
        query = '''
        MATCH (source:%s {name: '%s'})
        MATCH (target:%s {name: '%s'})
        MERGE (source)-[r:%s]->(target)
        ''' % (source_node_label,source_node,target_node_label, target_node, relationship_type)
        session.run(query)


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username == USER['username'] and password == USER['password']:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

# Logout route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
