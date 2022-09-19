import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content, tags, source) VALUES (?, ?, ?, ?)",
            ('First Post', 'Content for the first post', 'Tags for first post', 'source for first post')
            )

cur.execute("INSERT INTO posts (title, content, tags, source) VALUES (?, ?, ?, ?)",
            ('Second Post', 'Content for the second post', 'Tags for second post', 'source for second post')
            )


connection.commit()
connection.close()
