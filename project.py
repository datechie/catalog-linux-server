#!/usr/bin/python2.7.12
from flask import Flask
from flask import render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup_catalog import Category, Base, CategoryItem, User
from datetime import timedelta, datetime
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('/var/www/catalog/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

#engine = create_engine('sqlite:///catalog.db')
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Copying the user login and JSON details from the course Restaurnt project
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('/var/www/catalog/fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('/var/www/catalog/fb_client_secrets.json', 'r').read())['web']['app_secret']

    # Breaking the URL into multile parts to fit the pep8 guidelines
    p1 = 'https://graph.facebook.com/oauth/access_token?grant_type='
    p2 = 'fb_exchange_token&client_id=%s' % app_id
    p3 = '&client_secret=%s&' % app_secret
    p4 = 'fb_exchange_token=%s' % access_token
    url = p1 + p2 + p3 + p4
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s' % token
    url += '&fields=name,id,email'
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s' % token
    url += '&redirect=0&height=200&width=200'
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('The user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON for Catalog routes
@app.route('/catalog.json')
def catalogJSON():
    all_categories = session.query(Category).all()
    category_items = [category.serialize for category in all_categories]
    return jsonify(Category=category_items)


@app.route('/')
@app.route('/catalog/')
def showCategories():
    category = session.query(Category).all()
    # Using a join to get the details about recently added items and
    # the corresponding categories
    latest_items = session.query(Category, CategoryItem). \
        join(CategoryItem). \
        order_by(desc(CategoryItem.id)).\
        limit(10)
    if 'username' not in login_session:
        return render_template(
            'homepublic.html',
            category=category,
            latest_items=latest_items)
    else:
        return render_template(
            'home.html',
            category=category,
            latest_items=latest_items)


@app.route('/catalog/<category_name>/items')
def showCategoryItems(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    all_categories = session.query(Category).all()
    items = session.query(CategoryItem).filter_by(category_id=category.id)
    item_count = items.count()
    return render_template(
        'category.html',
        category=category,
        items=items,
        item_count=item_count,
        all_categories=all_categories)


@app.route('/catalog/<category_name>/<item>')
def showItemDetails(category_name, item):
    # Since the path has the item name and we want description
    # let us get the parent first ...
    thisItem = session.query(CategoryItem).filter_by(name=item).one()
    # ... and then from it get the description
    description = thisItem.description
    if 'username' not in login_session:
        return render_template(
            'itemspublic.html',
            item=item,
            description=description)
    else:
        return render_template(
            'items.html',
            item=item,
            description=description)


# Add a new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = CategoryItem(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['comp_select'],
            user_id=login_session['user_id'])
        session.add(newItem)
        flash('New Item %s Successfully Created' % newItem.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template(
            'newitem.html',
            categories=session.query(Category).all())


# Edit an item
@app.route('/catalog/<item>/edit/', methods=['GET', 'POST'])
def editCatalogItem(item):
    editedItem = session.query(CategoryItem).filter_by(name=item).one()
    category = session.query(
        Category).filter_by(id=editedItem.category_id).one()
    print("In edit item")
    if 'username' not in login_session:
        return redirect('/login')
    # If logged in user is not the one who created the item,
    # flash a message and go back to home page
    if editedItem.user_id != login_session['user_id']:
        msg = 'You are not authorized to edit %s.' % editedItem.name
        msg += ' Please create your own item in order to edit.'
        flash(msg)
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        if request.form['name'] or request.form['description']:
            editedItem.name = request.form['name']
            editedItem.description = request.form['description']
            editedItem.category_id = request.form['comp_select']
            flash('Successfully updated %s' % editedItem.name)
            session.commit()
            return redirect(url_for('showCategories'))
    else:
        return render_template(
            'editItem.html',
            editedItem=editedItem,
            category_name=category.name,
            categories=session.query(Category).all())


# Delete an item
@app.route('/catalog/<item>/delete/', methods=['GET', 'POST'])
def deleteItem(item):
    itemToDelete = session.query(CategoryItem).filter_by(name=item).one()
    if 'username' not in login_session:
        return redirect('/login')
    # If logged in user is not the one who created the item,
    # flash a message and go back to home page
    if itemToDelete.user_id != login_session['user_id']:
        msg = 'You are not authorized to delete %s.' % itemToDelete.name
        msg += ' Please create your own item.'
        flash(msg)
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('%s Successfully Deleted ' % itemToDelete.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteitem.html', itemToDelete=itemToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have been successfully logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    #app.debug = True
    #app.run(host='0.0.0.0', port=5000)
    app.run()
