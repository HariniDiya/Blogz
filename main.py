from flask  import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Build-a-blog:buildablog@localhost:8889/Build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app) 

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(120)) 
    entry = db.Column(db.String(240)) 

    def __init__(self, title, entry):
        self.title= title
        self.entry= entry

#tasks_title = []
#tasks_entry = []
tasks = []

@app.route('/validate', methods=['POST','GET'])
def validate_inputs():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_title_error = ''
        if (blog_title==''):
            blog_title_error = ' Enter Blog title '
        #else:
        #    tasks_title.append(blog_title)
           
        blog_entry = request.form['blog_entry']
        blog_entry_error = ''
        if (blog_entry==''):
            blog_entry_error = ' Enter Blog description '
        #else:
        #    tasks_entry.append(blog_entry)

        if (not blog_title_error) and (not blog_entry_error) :
            new_task=Task(blog_title,blog_entry)
            db.session.add(new_task)
            db.session.commit()
            print("newly created id : " + str(new_task.id))
           # tasks = Task.query.all()

            return render_template('showblog.html',title="Blog details", task=new_task)
        else:
            return render_template('addblog.html',title="Build a blog", blog_title=blog_title,blog_title_error=blog_title_error,blog_entry_error=blog_entry_error)

@app.route('/blog', methods=['POST', 'GET'])
def show_blog():
    #blog_id = int(request.form['id'])
    blog_id = request.args.get('id')
    print("id received from form: " + str(blog_id))
    task = Task.query.get(blog_id)
    return render_template('showblog.html',title="Blog details", task=task)

@app.route('/', methods=['POST', 'GET'])
def frontpage():
    tasks = Task.query.all()
    return render_template('blog.html',title="Build a blog", tasks=tasks)

@app.route('/add', methods=['POST', 'GET'])
def addentry():
    return render_template('addblog.html',title="Build a blog", tasks=tasks)
if __name__ == '__main__':
    app.run()

