#!/usr/bin/env python


from cgitb import enable
enable()
from html import escape
from cgi import FieldStorage
import pymysql as db
from os import environ
from shelve import open
from http.cookies import SimpleCookie


print('Content-Type: text/html')
print()

header = '''
            <header>
                <h1> Streaming </h1>
                <nav>
                  <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="streaming.py">Browse</a></li>
                    <li><a href="login.py">Login</a></li>
                    <li><a href="register.py">Register</a></li>
                  </ul>
                </nav>
            </header>'''
page = """
<main>
   <p>You do not have permission to access this page.</p>
   <ul>
       <li><a href="register.py">Register</a></li>
       <li><a href="login.py">Login</a></li>
   </ul>
</main>
   """
form_data = FieldStorage()
username = ''
playlist = ''
song_id = ''

try:
    cookie = SimpleCookie()
    http_cookie_header = environ.get('HTTP_COOKIE')
    if http_cookie_header:
        cookie.load(http_cookie_header)
        if 'sid' in cookie:
            sid = cookie['sid'].value
            session_store = open('sess_' + sid, writeback=False)
            if session_store.get('authenticated'):
                username = (session_store.get('username'))

                playlist = escape(form_data.getfirst('playlist', ''))
                song_id = escape(form_data.getfirst('song_id', ''))

                try:
                    connection = db.connect('localhost', 'root', 'fordemc2', 'projects')
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""DELETE FROM playlists WHERE username=%s and playlist_name=%s and song_id=%s """, (username, playlist, song_id))
                    connection.commit()
                    result = '<p>Song successfully Removed from %s</p>' % playlist
                    cursor.close()
                    connection.close()
                except db.Error:
                    result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'
                header = '''
                            <header>
                                <h1> Streaming </h1>
                                <nav>
                                  <ul>
                                    <li><a href="protected_streaming.py">Browse</a></li>
                                    <li class="current"><a href="protected_library.py">Library</a></li>
                                    <li><a href="profile.py">%s</a></li>
                                    <li><a href="logout.py">Logout</a></li>
                                  </ul>
                                </nav>
                            </header>''' % session_store.get('username')
                page = """
                    <main>
                        %s
                        <p>
                            <a href="protected_library.py?playlist=%s">Back to library</a>
                            <a href="protected_streaming.py">Go to Browse more music</a>
                        </p>
                    </main>
                    <aside>
                    </aside>""" % (result, playlist)
            session_store.close()

except IOError:
    result = '<p>Sorry! We are experiencing problems at the moment.</p>'


print("""<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width"/>
            <meta charset="utf-8" />
            <title>Streaming</title>
            <link rel="stylesheet" href="styles.css" />
        </head>
        <body>
            %s
            %s
        </body>
    </html>""" % (header, page))