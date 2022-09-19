import os
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from markupsafe import escape
from datetime import date

# 
from nltk.tokenize import word_tokenize
from nltk.text import Text

# import for transcription
from utils import *
from transcribe import *
from nlpai import *
import json


# new for "upload"
app = Flask(__name__)

# "running on ... http://127.0.0.1:5000/

def get_db_connection():
    conn = sqlite3.connect('dima-daten.db')
    conn.row_factory = sqlite3.Row
    return conn

def log_tracking(route, action):
    
    conn = get_db_connection()
    entry_max_id = conn.execute('SELECT * FROM tracking ORDER BY id DESC LIMIT 1').fetchone()
    log_id = entry_max_id['id']+1
        
    today = str(date.today())
    user='-'
    conn.execute('INSERT INTO tracking(id, date, user, route, action) VALUES (?, ?, ?, ?, ?)',
                         (log_id, today, user,	route, action))
    conn.commit()
    conn.close()
    return





def wordcount(stichwort):
    # username = request.cookies.get('username')
    liste = [] # liste der erfolgreichen Suchergebnisse
    conn = get_db_connection()
    entries = conn.execute('SELECT * FROM entries').fetchall()
    # stichwort = 'great'
    conn.close()
    
    # print('!!!')

    k=0
    score=0
    subentries = []
    for entry in entries:
       print(k)
       k=k+1
       print(entry['content'])

       if stichwort in entry['content']:
          print('gefunden ! \n')
          score = score+1
          liste.append(entry['id'])
          subentries.append(entry)
       # else:
       #   print('nix')
    
    print('score:', score, '\n -------------------- \n')  
    # print('\n -------------------- \n')
    return score, liste, subentries


def get_entry(entry_id):
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM entries WHERE id = ?',
                        (entry_id,)).fetchone()
    conn.close()
    if entry is None:
        abort(404)
    return entry


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# --- for uploading:
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





# --- routing

@app.route('/')
def index(): 
    conn = get_db_connection()
    entries = conn.execute('SELECT * FROM entries').fetchall()
    conn.close()
    return render_template('index.html', entries=entries)


@app.route('/<int:entry_id>')
def entry(entry_id):
    log_tracking('/<int:entry_id>', entry_id)
    print('\n\n\n.................... 1')
    entry = get_entry(entry_id)
    print('\n\n\n.................... 2')    
    return render_template('entry.html', entry=entry)


@app.route('/q=<int:entry_id>')
def show_json(entry_id):
    log_tracking('q=<int:entry_id>', entry_id)
    # print('\n\n\n.................... 1')
    entry = get_entry(entry_id)
    # print(entry)
    # print('\n\n\n.................... 2')  
      
    
    # print(json.dumps(entry))
    
    # print('\n\n\n.................... 3')  
    
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM entries WHERE id=?;", [entry_id]).fetchall()    
    # print(data)
    data = [tuple(row) for row in data]
    print(data)
    
    
    # conn.execute("SELECT * FROM sqlite_master WHERE " \
    #      "tbl_name='your_table_name' AND type = 'table'")
    # create_table_string = cursor.fetchall()[0][0]
    # print('\n\n\n.................... 4')  
    
    return json.dumps(data)



#
#
# ...hier Eingabemaske anpassen
#
#

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        theme = request.form['theme']
        content = request.form['content']
        keywords = request.form['keywords']
        source = request.form['source']
        entry_id = 999; 
        # nickname = request.form['nickname']
        # phone = request.form['phone']
            
        if not content:
            flash('Inhalt ist erforderlich!')
        else:            
            conn = get_db_connection()
            entry_max_id = conn.execute('SELECT * FROM entries ORDER BY id DESC LIMIT 1').fetchone()
            entry_id = entry_max_id['id']+1
            print('entry_id :', entry_id  )
            log_tracking('/create', entry_id)
            
            conn.execute('INSERT INTO entries (id, theme, content, keywords, source) VALUES (?, ?, ?, ?, ?)',
                         (entry_id, theme, content, keywords, source))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')






@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    log_tracking('/<int:id>/edit', id)    
    print('-------------------------------------------------- 1')
    entry = get_entry(id)

    if request.method == 'POST':
        theme = request.form['theme']
        content = request.form['content']
        keywords = request.form['keywords']
        source = request.form['source']

        print('-------------------------------------------------- 2')
        if not theme:
            flash('Theme is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE entries SET theme = ?, content = ?, keywords = ?, source = ?'
                         ' WHERE id = ?',
                         (theme, content, keywords, source, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

        print('-------------------------------------------------- 3')
    return render_template('edit.html', entry=entry)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    '/<int:id>/edit'  
    log_tracking('/<int:id>/delete', id)       
    entry = get_entry(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM entries WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(entry['theme']))
    return redirect(url_for('index'))

@app.route('/entry/<int:entry_id>')
def show_entry(entry_id):
    log_tracking('/entry/<int:entry_id>', entry_id) 
    # show the post with the given id, the id is an integer
    return f'Post {entry_id}'


# ---------------------------------------------------------------------
# tags, about
       
@app.route('/void')
def void():
    log_tracking('/void', '-') 
    return render_template('void.html')
       

    
@app.route('/about')
def about():
    log_tracking('/about', '-')     
    return render_template('about.html')



@app.route('/found')
def found():
   log_tracking('/found', '-')     
   # return 'tagging'
   return render_template('found.html')
    
# ---------------------------------------------------------------------

# search


@app.route('/search', methods=('GET', 'POST'))
# @app.route('/search')
def search():
    stichwort = 'great'
    if request.method == 'POST':        
        stichwort = request.form['stichwort']

        print('Stichwort: ', stichwort, '\n')

        if not stichwort:
            flash('Stichwort eingeben!')
        else:
            # conn = get_db_connection()
            # entries = conn.execute('SELECT * FROM entries').fetchall()
            # conn.close()
            log_tracking('/search', stichwort) 
            score, liste, entries = wordcount(stichwort)
            print('SCORE', score, '-------------', liste)


        # return render_template('found.html', stichwort=stichwort,score=score, liste=liste, subentries=subentries)
        return render_template('search.html', stichwort=stichwort,score=score, liste=liste, entries=entries)
    
        # return render_template('found.html', counter=counter)
    return render_template('search.html')





# ----------------- uploading ---------------

@app.route('/upload', methods=('GET', 'POST'))
def upload():
# def upload_files():
 

    app.config['UPLOAD_EXTENSIONS'] = ['.pdf', '.png', '.gif']
    app.config['UPLOAD_PATH'] = 'uploads'

    # print('..............\n ..............\n ..............\n')
    if request.method == 'POST':
        print('A..............')

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            # return redirect(request.url)
            return render_template('upload.html')            
        file = request.files['file']
        log_tracking('/upload', file) 
        
        if file.filename == '':
            flash('No file selected for uploading')
            # return redirect(request.url)
            return render_template('upload.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return render_template('upload.html')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)                  

        return render_template('upload.html')
    
    print('B..............')        

    return render_template('upload.html')


# ----------------- transcription ---------------

@app.route('/trans')
def trans():
    log_tracking('/trans', '-')     
    print('....transcribieren')
    paragraphs = transai()  
    return render_template('trans.html',paragraphs=paragraphs)


# ----------------- nlp ---------------

@app.route('/nlp')
def nlp():
    log_tracking('/nlp', '-')     
    print('....NLP...')
    filename='uploads/brandon.txt' 

    with open(filename) as f:
        contents = f.read()
        # print(contents)

    text = Text(word_tokenize(contents))
    tag='keine'
    # clist = text.concordance(tag)
    clist = text.concordance_list("Leute")

    hlist=[]
    for k in range(len(clist)):
        hlist.append(clist[k][-1])

    # colocation list
    tokens = word_tokenize(contents)
    text = Text(tokens)
    coloc=text.collocation_list()
    print(coloc)

    # clist = nlpai(filename)

    # return render_template('nlp.html')
    return render_template('nlp.html', hlist=hlist, coloc=coloc)




# ---------------------------------------------------------------------

# nlp_search

@app.route('/nlp_search', methods=('GET', 'POST'))
# @app.route('/nlp_search')
def nlp_search():
    log_tracking('/nlp_search', '-')     
    if request.method == 'POST':        
        stichwort = request.form['stichwort']

        print('Stichwort: ', stichwort, '\n')

        if not stichwort:
            flash('Stichwort eingeben!')
        else:
            conn = get_db_connection()
            entries = conn.execute('SELECT * FROM entries').fetchall()
            conn.close()

            nummern=range(len(entries))
            scorelist=[]
            for entry in entries:
                print(entry['content'],'\n --------- ')

                tokens = word_tokenize(entry['content'])
                text = Text(tokens)
                anzahl=text.count(stichwort)
                print('Anzahl:', anzahl, '\n\n\n')
                scorelist.append(anzahl)

            # score, liste = wordcount(stichwort)
            # print('SCORE', score, '-------------', liste)

        return render_template('nlp_found.html', stichwort=stichwort, nummern=nummern, scorelist=scorelist)
        # return render_template('nlp_found.html', variable='123456')
        # return render_template('nlp_found.html', stichwort=stichwort,score=score, liste=liste)
 
    return render_template('nlp_search.html')


# ---------------------------------------------------------------------

@app.route('/filter')
def filter():
    log_tracking('/filter', '?')     
    conn = get_db_connection()
    entries = conn.execute('SELECT * FROM entries').fetchall()
    conn.close()
    return render_template('filter.html', entries=entries)    
    
    # print('....filtering')
    # return render_template('filter.html')


# ---------------------------------------------------------------------

@app.route('/table')
def table():
    log_tracking('/table', '-')     
    print('....table')
    
    conn = get_db_connection()
    tracking = conn.execute('SELECT * FROM tracking').fetchall()
    conn.close()    
    
    
    
    return render_template('table.html', tracking=tracking)

# ---------------------------------------------------------------------

def get_categories_and_keywords(category):
    # categories and keywords
    # ... not sure what is the implementation that works for both keywords and categories
    conn = get_db_connection()    
    categories = conn.execute('SELECT * FROM categories').fetchall()
    # ! reinterpretation of format of variables !
    # ! needs category 
    cat = conn.execute('SELECT * FROM categories WHERE category = ?', (category,)).fetchone()
    keywords = cat['keywords'].split(", ")
    conn.close()
    
    return categories, keywords

    
@app.route('/category/<category>')
def category(category):
    log_tracking('/category', category)     
    print('....', category)
    
    
    print('.... 0')    
    conn = get_db_connection()
    entries = conn.execute('SELECT * FROM entries WHERE category = ?',
                        (category,)).fetchall()  

    conn.close()


    # conn = get_db_connection()    
    # categories = conn.execute('SELECT * FROM categories').fetchall()
    # ! reinterpretation of format of variables !
    # ! needs category 
    # cat = conn.execute('SELECT * FROM categories WHERE category = ?', (category,)).fetchone()
    # keywords = cat['keywords'].split(", ")    
    # conn.close()    
    #
    # print('.... 1')
    categories, keywords = get_categories_and_keywords(category)
    # print('.... 2')    
    
    return render_template('category.html', category=category, entries=entries, categories=categories, keywords=keywords)






@app.route('/keyword/<keyword>')
def keyword(keyword):
    log_tracking('/keyword', keyword)     
    print('....', keyword)
    
    conn = get_db_connection()
    entries = conn.execute("SELECT * FROM entries WHERE keywords LIKE '%'||?||'%'", (keyword,)).fetchall() 
    print('2...')
    ### category  = conn.execute("SELECT * FROM categories WHERE keywords LIKE '%'||?||'%'", (keyword,)).fetchone()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    #### - category = category('category') # ! this is the trick
    #### categories, keywords = get_categories_and_keywords(category)
    return render_template('keyword.html', keyword=keyword, entries=entries, categories=categories)





# ---------------------------------------------------------------------

@app.route('/sandbox')
def sandbox():
    log_tracking('/sandbox', '-')     
    print('....sandbox')
 
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()

    for category in categories:
        print(category['category'], '\t', category['keywords'], '\n')
    
    
    
    klist = category['keywords'].split(", ")

    return render_template('sandbox.html', categories=categories, klist=klist)






