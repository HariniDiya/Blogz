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
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
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
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            #return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            # TODO - "remember" the user
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"
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

            return render_template('showblog.html',title="Blog details", task=new_task)
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
    return render_template('showblog.html',title="Blog details", task=task)

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

