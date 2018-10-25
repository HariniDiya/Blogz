from flask  import Flask, request, redirect, render_template, session, flash

from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(120)) 
    entry = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

    def __init__(self, title, entry,owner):
        self.title= title
        self.entry= entry
        self.owner= owner
tasks = []

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    #allowed_routes = ['login', 'signup', 'frontpage','blogzpage','show_blog']
    #if request.endpoint not in allowed_routes and 'username' not in session:
    allowed_routes = ['addentry']
    if request.endpoint in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            #return redirect('/')
            return redirect('/add')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        username_error = ''
        if (username=='' or len(username) < 3 or len(username) > 20):
            username_error = ' Invalid User Name '
        elif (' ' in username) == True:
            username_error = ' Invalid User Name '
        password = request.form['password']
        password_error = ''
        if (password=='' or len(password) < 3 or len(password) > 20):
            password_error = ' Invalid Password '
        elif (' ' in password) == True:
            password_error = ' Invalid password '
        verify = request.form['verify']
        verify_password_error = ''
        if (verify!= password):
            verify_password_error = ' Password does not match '  

        existing_user = User.query.filter_by(username=username).first()
        # if the username already exists and username_error not already present 
        if existing_user and (not username_error): 
            username_error = ' User Name already exists'
        if (not username_error) and (not password_error) and (not verify_password_error) and (not existing_user):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            #return redirect('/')
            return redirect('/add')
        else:
            return render_template('signup.html',title="Blogz", username=username,
            username_error=username_error,passsword=password,password_error=password_error,
            verify=verify,verify_password_error=verify_password_error)
    return render_template('signup.html')

@app.route('/validate', methods=['POST','GET'])
def validate_inputs():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_title_error = ''
        if (blog_title==''):
            blog_title_error = ' Enter Blog title '   
        blog_entry = request.form['blog_entry']
        blog_entry_error = ''
        if (blog_entry==''):
            blog_entry_error = ' Enter Blog description '
        #else:
        #    tasks_entry.append(blog_entry)

        if (not blog_title_error) and (not blog_entry_error) :
            new_task=Task(blog_title,blog_entry,owner)
            db.session.add(new_task)
            db.session.commit()

            print("newly created id : " + str(new_task.id))
           # tasks = Task.query.all()

            return render_template('showblog.html',title="Blog details", task=new_task, user=owner)
        else:
            return render_template('addblog.html',title="Build a blog", blog_title=blog_title,blog_title_error=blog_title_error,blog_entry_error=blog_entry_error)

@app.route('/', methods=['POST', 'GET'])
def frontpage():
    users = User.query.all()
    return render_template('index.html',title="Blogz", users=users)
    
@app.route('/blog', methods=['POST', 'GET'])
def show_blog():
    #blog_id = int(request.form['id'])
    blog_id = request.args.get('id')
    print("id received from form: " + str(blog_id))
    task = Task.query.get(blog_id)
    #getting user information
    user = User.query.get(task.owner_id)
    return render_template('showblog.html',title="Blog details", task=task,user=user)

@app.route('/blogz', methods=['POST', 'GET'])
def blogzpage():
    user_id = request.args.get('userid')
    if user_id:
        user = User.query.get(user_id)
        tasks = user.tasks
    else:
        tasks = Task.query.all()
    return render_template('blog.html',title="Build a blog", tasks=tasks)
    

@app.route('/add', methods=['POST', 'GET'])
def addentry():
    return render_template('addblog.html',title="Build a blog", tasks=tasks)
if __name__ == '__main__':
    app.run()

