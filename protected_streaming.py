#!/usr/bin/env python


from cgitb import enable
enable()
from html import escape
from cgi import FieldStorage
import pymysql as db
from os import environ
from shelve import open
from http.cookies import SimpleCookie


print("Content-type: text/html")
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
search = ''
form_data = FieldStorage()
new_playlist = ''
playlists = '<option value="my_playlist">my_playlist</option>'
sort = ''
genre = ''


try:
    cookie = SimpleCookie()
    http_cookie_header = environ.get('HTTP_COOKIE')
    if http_cookie_header:
        cookie.load(http_cookie_header)
        if 'sid' in cookie:
            sid = cookie['sid'].value
            session_store = open('sess_' + sid, writeback=False)
            if session_store.get('authenticated'):
                username = session_store.get('username')
                try:
                    connection = db.connect('localhost', 'root', 'fordemc2', 'projects')
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT DISTINCT playlist_name FROM playlists where username=%s""", username)

                    if cursor.rowcount != 0:
                        playlists = ''
                        for row in cursor.fetchall():
                            playlists += '<option value="%s">%s</option>' % (row['playlist_name'], row['playlist_name'])

                    cursor.execute("""SELECT * FROM music""")
                    result = """
                            <audio controls source src='' type='audio/mp3' id='audioPlayer' >
                                <p>Sorry, Your browser doesn't support HTML5</p>
                            </audio>
                            <table id='songlist'>
                                <tr><th colspan="3">All Music</th></tr>
                                <tr><th>Name</th><th>Artist</th><th>Add to playlist</th></tr>"""

                    for row in cursor.fetchall():
                        result += """<tr>
                                            <td><a href='%s'>%s</a></td>
                                            <td>%s</td>
                                            <td>
                                            <form action='protected_add_to_playlist.py?song_id=%s' method='post'>
                                                <select name="playlist">
                                                    %s
                                                </select>
                                                <input type="submit" value='Add'/>
                                            </form>
                                            </td>
                                    </tr>""" % (row['location'], row['name'], row['artist'], row['song_id'], playlists)
                    result += '</table>'
                    cursor.close()

                    if len(form_data) != 0:

                        genre = escape(form_data.getfirst('genre', '')).strip()
                        sort = escape(form_data.getfirst('sort', '')).strip()
                        new_playlist = escape(form_data.getfirst('new_playlist', '')).strip()
                        search = escape(form_data.getfirst('search', ''))

                        genre_selection = ['rock', 'punk', 'hiphop', 'electric', 'freaky', '']
                        sort_selection = ['song_id', 'artist', 'name', 'date_of_release']

                        cursor = connection.cursor(db.cursors.DictCursor)

                        if new_playlist != '':
                            cursor.execute("""INSERT INTO playlists (username, playlist_name)
                                    VALUES (%s, %s)""", (username, new_playlist))
                            connection.commit()
                            cursor.execute("""SELECT DISTINCT playlist_name FROM playlists
                            where username=%s""", username)

                            if cursor.rowcount > 1:
                                playlists = ''
                                for row in cursor.fetchall():
                                    playlists += '<option value="%s">%s</option>' % (row['playlist_name'], row['playlist_name'])

                            cursor.execute("""SELECT * FROM music""")

                        if search != '':
                            cursor.execute("""SELECT * FROM music where name = %s or artist = %s""", (search, search))

                        if genre in genre_selection and sort in sort_selection and search == '':
                            if genre == "":
                                cursor.execute("""SELECT * FROM music ORDER BY %s""" % sort)
                            elif sort == "song_id":
                                cursor.execute("""SELECT * FROM music WHERE genre = %s""", genre)
                            else:
                                cursor.execute("""SELECT * FROM music WHERE genre = '%s' ORDER BY %s""" % (genre, sort))

                        result = """
                                <audio controls source src='' type='audio/mp3' id='audioPlayer'>
                                    <p>Sorry, Your browser doesn't support HTML5</p>
                                </audio>
                                <table id='songlist'>
                                    <tr><th colspan="3">All Music</th></tr>
                                    <tr><th>Name</th><th>Artist</th><th>Add to playlist</th></tr>"""

                        for row in cursor.fetchall():
                            result += """<tr>
                                                <td><a href='%s'>%s</a></td>
                                                <td>%s</td>
                                                <td>
                                                <form action='protected_add_to_playlist.py?song_id=%s' method='post'>
                                                    <select name="playlist">
                                                        %s
                                                    </select>
                                                    <input type="submit" value='Add'/>
                                                </form>
                                                </td>
                                             </tr>""" % (
                                row['location'], row['name'], row['artist'], row['song_id'], playlists)
                        result += '</table>'
                        cursor.close()
                        connection.close()
                except db.Error:
                    result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

                header = '''
                            <header>
                                <h1> Streaming </h1>
                                <nav>
                                  <ul>
                                    <li class="current"><a href="protected_streaming.py">Browse</a></li>
                                    <li><a href="protected_library.py">Library</a></li>
                                    <li><a href="profile.py">%s</a></li>
                                    <li><a href="logout.py">Logout</a></li>
                                  </ul>
                                </nav>
                            </header>''' % username
                page = """
                    <main>
                            <form action='protected_streaming.py' method='get'>
                                <label for="search">Search: </label>
                                <input type="text" name="search" value="%s">
                                <label for="sort">Sort By: </label>
                                <select name="sort" id='sort'>
                                    <option value="song_id">All</option>
                                    <option value="artist">Artist</option>
                                    <option value="name">Song Name</option>
                                    <option value="date_of_release">Release Date</option>
                                </select>
                                <label for="genre">Pick a Genre: </label>
                                <select name="genre" id='genre'>
                                    <option value="">All</option>
                                    <option value="rock">Rock</option>
                                    <option value="hiphop">HipHop</option>
                                    <option value="punk">Punk</option>
                                    <option value="electric">Electric</option>
                                    <option value="freaky">Freaky</option>
                                </select>
                                <input type="submit" value='Search'/>
                            </form>
                        %s
                    </main>
                    <aside>
                        <h1>Adding a new Playlist</h1>
                        <article>
                            Below you can create a playlist and add music to it, you can do this by filling in the name
                            of the playlist you want to create into the box below entitled "Create a new playlist", 
                            after you have done that you can move over to the "Add to playlist" section of the 
                            music list, on each song theres and option to choose what playlist you would like to 
                            add the song to, if you do indeed want to add that song assuming you have choosen the 
                            perferred playlist, you just click "Add".
                        </article>
                        <form action='protected_streaming.py' method='get'>
                            <label for='add_playlist'>Create a new playlist:</label>
                            <input type='text' name='new_playlist' id='add_playlist'>
                            <input type="submit" value='Add'/>
                        </form>
                    </aside>""" % (search, result)
            session_store.close()
except IOError:
    page = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

print("""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width"/>
            <meta charset="utf-8" />
            <title>Streaming</title>
            <link rel="stylesheet" href="styles.css" />
            <script src="https://code.jquery.com/jquery-2.2.0.js"></script>
        </head>
        <body>
            %s
            %s
            <script>
                    audioPlayer();
                      function audioPlayer(){
                        var currentSong = 0;
                        $('#audioPlayer')[0].src = $('#songlist tr td a')[0];
                        $('#songlist tr td a').click(function(e){
                          e.preventDefault();
                          $('#audioPlayer')[0].src = this;
                          $('#audioPlayer')[0].play();
                          $('#songlist tr td').removeClass('current_song');
                          currentSong = $(this).parent().index();
                          $(this).parent().addClass('current_song');
                        });
                      }
            </script>
        </body>
    </html>""" % (header, page))
