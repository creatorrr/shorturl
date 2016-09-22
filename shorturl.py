#!/bin/env python3

from flask import flash, Flask, request, redirect, render_template, url_for
from os import urandom
import logging
import random
import redis
import string


# Create application object and read config from config.py
app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY'] = urandom(app.config['KEYLENGTH'])

redis = redis.Redis(host=app.config['REDISHOST'],
                    port=app.config['REDISPORT'],
                    db=app.config['REDISDB'],
                    password=app.config['REDISPASSWD'])


def GetExpSeconds(unit, value):
    """ Function accepting a time unit and value to convert into seconds.
        This is used as redis expiration values are in seconds only. """

    if unit == 'seconds':
        return value
    elif unit == 'minutes':
        return (60 * value)
    elif unit == 'hours':
        return (60 * 60 * value)
    else:
        return 0    # Invalid input results in the key set to never expire.


def GenShortKey(length=8):
    """ Function to generate a short random string to use as a key to build
        the short URLs. Default is 8 characters in length. """

    validchars = string.ascii_letters + string.digits
    shortkey = ''

    for i in range(length):
        shortkey += random.SystemRandom().choice(validchars)

    return shortkey


def GetFullURL(key):
    """ Get value for specified key. This should be a valid URL. """

    # Attempt to get the full URL, will return None if key does not exist
    try:
        return redis.get(key).decode('utf-8')
    # Return None on any exception in the event of any exception
    except:
        return None


def InsertData(shorturl, fullurl, expiration=0):
    """ Insert key and full URL into the database for later access.
        Value of 0 results in no expiration of the key. """

    try:
        # Set expiration for key to remove shot URL after x seconds
        if expiration == 0:
            # Set the key only if it does not exist to prevent overwriting
            # exisitng URL data.
            redis.set(shorturl, fullurl)
        elif expiration > 0:
            redis.setex(shorturl, fullurl, expiration)

        return True
    except:
        return False


@app.route('/')
def ShowIndex():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def InsertRoute():
    siteurl = app.config['SITEURL']

    furl = request.form['fullurl']
    expunit = request.form['expunit']

    expval = 0
    if request.form['expval']:
        expval = int(request.form['expval'])

    expiration = GetExpSeconds(expunit, expval)

    # Use KEYLENGTH setting if available otherwise use the default length of 8
    if app.config['KEYLENGTH']:
        skey = GenShortKey(app.config['KEYLENGTH'])
    else:
        skey = GenShortKey()

    # If trailing / is not present add it to ensure a valid URL
    if siteurl.endswith('/'):
        surl = siteurl + skey
    else:
        surl = siteurl + '/' + skey

    if InsertData(skey, furl, expiration):
        return render_template('index.html', fullurl=furl, shorturl=surl)
    else:
        flash('Error encountered saving data')
        return redirect(url_for('ShowIndex'))


@app.route('/<urlkey>')
def ExpandURL(urlkey):
    """ Attempt to open the URL matching the provided key. """

    furl = GetFullURL(urlkey)
    if furl:
        return redirect(furl)
    else:
        flash('Redirect failed: Invalid or missing short URL')
        return redirect(url_for('ShowIndex'))


@app.route('/<urlkey>/preview')
def ViewURL(urlkey):
    """ Using the preview option will allow for review of the full URL
        matching the given key. """

    furl = GetFullURL(urlkey)

    if furl:
        surl = app.config['SITEURL'] + '/' + urlkey
        return render_template('preview.html', fullurl=furl, shorturl=surl)
    else:
        flash('Preview failed: invalid or missing key')
        return render_template('index.html')


if __name__ == '__main__':
    app.run(app.config['LISTENHOST'], app.config['LISTENPORT'], debug=True)
