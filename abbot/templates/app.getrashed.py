import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from markupsafe import escape
# "running on ... http://127.0.0.1:5000/


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/')
def index():
    # username = request.cookies.get('username')
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


# ---------------------------------------------------------------------
# search


@app.route('/search')
def search():
    # username = request.cookies.get('username')
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    stichwort = 'great'
    conn.close()

    print('!!!')
    
    k=0
    score=0
    for post in posts:
       print(k)
       k=k+1
       print(post['content'])

       if 'great' in post['content']:
          print('gefunden ! \n')
          score = score+1
       else:
          print('nix')
    
    print('score:', score, '\n -------------------- \n')
    # print('\n -------------------- \n')

    if request.method == 'POST':
        stichwort = request.form['stichwort']

        if not stichwort:
            flash('Stichwort eingeben!')
        else:	    
            conn = get_db_connection()
            posts = conn.execute('SELECT * FROM posts').fetchall()
            conn.close()

            # return render_template('found.html', posts, stichwort)
        return render_template('about.html')

    return render_template('search.html')
   


# ---------------------------------------------------------------------
# tags, about

@app.route('/void')
def voidy():
    return render_template('void.html')

@app.route('/tags')
def tags():
    # return 'tagging'
    return render_template('tags.html')

@app.route('/about')
def about():

    return render_template('about.html')
    #
    # return render_template('about.html', posts=posts)
    # return 'dima KI'

# app.route('/found')
# def found():
#   # return 'tagging'
#   return render_template('found.html')

# ---------------------------------------------------------------------



@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)



@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


# from "quickstart"
@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


def hell0():
    return 'Hello, World'


# @app.route('/login')
# def login():
#    return 'login'


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#    if request.method == 'POST':
#        return do_the_login()
#    else:
#        return show_the_login_form()


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
 
    return render_template('login.html', error=error)
    # return render_template('create.html')

    # return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/var/www/uploads/uploaded_file.txt')





@app.route('/user/<username>')
def profile(username):
    # show the user profile for that user
    print(url_for('login'))
    print('log comment')
    # print(url_for('profile', username='John Doe'))
    return f'User-Benutzer {escape(username)}'


with app.test_request_context():
    print('xxx---xxx\n\n\n')
    print(url_for('login'))
    print(url_for('profile', username='John Doe'))

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'

@app.route('/projects/')
def projects():
    return 'The project page'


# for some reason the route is not recognized
@app.route('/bot', methods=['POST'])
def bot():
   print('BOT')
   return 'The bot'

@app.route('/other', methods=['POST'])
def other():
   # The method is not allowed for the requested URL.
   # incoming_msg = request.values.get('Body', '').lower()
   # resp = MessagingResponse()
   # msg = resp.message()


   incoming_msg='wo ist ein Zitat ??'

   responded = False
   if 'zitat' in incoming_msg:
       # return a quote
       r = requests.get('https://api.quotable.io/random')
       if r.status_code == 200:
           data = r.json()
           quote = f'{data["content"]} ({data["author"]})'
       else:
           quote = 'Bitte entschuldigen Sie. Ich konnte kein Zitat finden.'
       msg.body(quote)
       responded = True
   if 'katze' in incoming_msg:
       # return a cat pic
       msg.media('https://cataas.com/cat')
       responded = True
   if not responded:
       msg.body('Ich kenne mich leider nur mit Zitaten und Katzen aus.')
   return str(resp)
   


@app.route("/<name>")
def escape_route(name):
   return f"Hello, {escape(name)}!"
