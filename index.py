from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
import sqlite3


def sql(sql, data=''):
    c = sqlite3.connect('database.db')
    conn = c.execute(sql, data)
    c.commit()
    return conn


def init():
    posts = '''
      CREATE TABLE
      IF NOT EXISTS posts (
         id integer PRIMARY KEY,
         title text NOT NULL,
         post text,
         date data
         );
         '''
    sql(posts)


init()
app = Flask(__name__)


@app.route('/<int:post_id>')
def show_post(post_id):
    post = sql('select id,title,post,date from posts where id=?',
               [str(post_id)])
    x = [dict(xid=r[0], title=r[1], post=r[2], date=r[3]) for r in post]
    return render_template('show.html', post=x)


@app.route('/')
def index():
    count = sql('select count(*) from posts')
    c = count.fetchone()[0]
    posts = sql('select * from posts limit 5')
    x = [dict(xid=row[0], title=row[1], post=row[2]) for row in posts]
    return render_template('index.html', posts=x, count=c)


@app.route('/next')
def next():
    posts_num = request.args.get('n', int)
    count = sql('select count(*) from posts')
    c = count.fetchone()[0]
    posts = sql('select * from posts limit 5 offset ?', [str(posts_num)])
    x = [dict(xid=r[0], title=r[1], post=r[2]) for r in posts]
    return render_template('index.html', posts=x, count=c)


@app.route('/new')
def new():
    return render_template('post.html')


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    # update it
    edit = request.form['edit']
    if edit == "edit":
            post = sql('select id,title,post from posts where id=?',
                       [str(post_id)])
            x = [dict(xid=r[0], title=r[1], post=r[2]) for r in post]
            return render_template('edit.html', post=x)

    if edit == "delete":
            sql('delete from posts where id=?', [str(post_id)])
            return redirect(url_for('index'))


@app.route('/edited', methods=['GET', 'POST'])
def edited():
    title = request.form['title']
    new_post = request.form['post']
    post_id = request.form['id']
    post = sql('update posts set title=? , post=? where id=?',
               [title, new_post, str(post_id)])
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        q = request.form['q'].encode('utf-8')
        n = request.form['n']
    except:
        q = request.args.get('q').encode('utf-8')
        n = request.args.get('n')
    s = sql('''select * from posts
            where title like '%{t}%' or post like '%{t}%'
            limit 5 offset ?'''.format(t=q), [n])

    x = [dict(xid=r[0], title=r[1], post=r[2]) for r in s]
    count = sql('''select count(*) from posts
                where title like '%{t}%' or post like '%{t}%' '''.format(t=q))
    c = count.fetchone()[0]
    return render_template('index.html', posts=x, q=q.decode('utf-8'), count=c)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    title = request.form['title']
    post = request.form['post']
    sql('''insert into posts(id,title,post,date)
        values((select max(id) + 1 from posts),?,?,datetime('now'));''',
        (title, post))
    return redirect(url_for('index'))
