from flask import (
                   Flask,
                   jsonify,
                   request,
                   url_for,
                   redirect,
                   abort,
                   g,
                   render_template,
                   make_response,
                   flash,
                   session as login_session,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, asc, desc
from models import Base, User, Category, Item
from flask_httpauth import HTTPBasicAuth
from flask_login import (
                LoginManager,
                login_user,
                logout_user,
                current_user,
                login_required,
)
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
import json
import random
import string

engine = create_engine('sqlite:///cat_app_data.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'showLogin'

CLIENT_ID = json.loads(open('g_auth.json', 'r').read())['web']['client_id']


@app.before_request
def before_request():
    g.user = current_user


@app.route('/token')
@login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


# Google Login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the auth code into a credentials object
        oauth_flow = flow_from_clientsecrets('g_auth.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
                      json.dumps(
                        'Failed to upgrade the authorization code.'),
                      401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the acces token info...abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
                    json.dumps(
                        'Token user ID does not match given user ID'),
                    401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for the app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
                    json.dumps(
                        'Token client id does not match app id'),
                    401)
        response.headers['Content-Type'] = 'application/json'
        return reponse

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
                    json.dumps(
                        'Current user is already connected'),
                    200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later user
    login_session['provider'] = 'google'
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

    # See if user exists, if not...create a new user
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Log user into the login manager
    user = session.query(User).filter_by(id=user_id).one()
    login_user(user)

    flash("Successful log on via Google")
    # Welcome the user
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style="width:100px;height:100px;'
    output += 'border-radus:50px;'
    output += '-webkit-border-radius:50px;'
    output += '-moz-border-raidus:50px;">'
    print "Google login completed"
    return output


# DISCONNECT (Google) - Revoke current user token and reset
#                       their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
                    json.dumps(
                        'Current user not connected.'),
                    401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        # The token was invalid
        response = make_response(
                    json.dumps(
                        'Faild to revoke the token for given user.'),
                    400)
        response.headers['Content-Type'] = 'application/json'
        return response
    print "Logged out of Google account"


# API Endpoints
@app.route('/catalog.json/')
def apiCatalogJSON():
    cat_items = session.query(Category).all()
    return jsonify(Catalog=[i.serialize for i in cat_items])


# Web routing
@app.route('/')
@app.route('/catalog/', methods=['GET'])
def homePage():
    user = g.user
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(10)
    if items:
        return render_template('main.html', categories=categories, items=items)
    else:
        return render_template('main.html', categories=categories)


@app.route('/catalog/<string:category>/items/')
def showCategory(category):
    categories = session.query(Category).all()
    items = (
        session.query(
            Item
        )
        .join(Category)
        .filter(Category.name == str(category))
        .all()
    )
    if items:
        print "Should be rendering items in a category"
        return render_template('categories.html',
                               categories=categories,
                               items=items,
                               cur_cat=category)
    else:
        return render_template('categories.html',
                               categories=categories,
                               cur_cat=category)


@app.route('/catalog/<string:category>/<string:item_name>/')
def showItem(category, item_name):
    item = session.query(Item).filter(Item.title == str(item_name)).first()
    return render_template('itemDescription.html', item=item)


@app.route('/catalog/add/', methods=['GET', 'POST'])
@login_required
def addItem():
    categories = session.query(Category).all()
    if request.method == 'GET':
        return render_template('addItem.html', categories=categories)
    if request.method == 'POST':
        form_title = request.form.get('title', None)
        form_description = request.form.get('description', None)
        form_category = request.form.get('cat_select', 'Misc.')
        if (
            form_title is None or
            form_description is None or
            form_category is None
        ):
            error = "Title, description, and category are all required"
            return render_template('addItem.html',
                                   categories=categories,
                                   error=error)
        category = session.query(
                        Category
                   ).filter_by(name=form_category).first()
        newItem = Item(title=request.form['title'],
                       description=request.form['description'],
                       category_id=category.id,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("Item Added")
        return redirect(url_for('homePage'))


@app.route('/catalog/<string:item_name>/edit/', methods=['GET', 'POST'])
@login_required
def editItem(item_name):
    item = session.query(Item).filter_by(title=item_name).first()
    categories = session.query(Category).all()
    if int(login_session['user_id']) != int(item.user_id):
        return render_template('notAuthorized.html')
    if request.method == 'GET':
        return render_template('editItem.html',
                               categories=categories,
                               item=item)
    if request.method == 'POST':
        newItem = item
        if request.form['title']:
            newItem.title = request.form['title']
        if request.form['description']:
            newItem.description = request.form['description']
        if request.form['cat_select']:
            category_selected = request.form['cat_select']
            category_for_item = session.query(
                                    Category
                                ).filter_by(name=category_selected).first()
            newItem.category_id = category_for_item.id
        session.add(newItem)
        session.commit()
        flash("Item Edited")
        return render_template('itemDescription.html', item=newItem)


@app.route('/catalog/<string:item_name>/delete/', methods=['GET', 'POST'])
@login_required
def deleteItem(item_name):
    item = session.query(Item).filter(Item.title == str(item_name)).first()
    current_category = item.category.name
    if int(login_session['user_id']) != int(item.user_id):
        return render_template('notAuthorized.html')
    if request.method == 'GET':
        return render_template('deleteItem.html', i_name=item_name)
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item Deleted")
        return redirect(url_for('homePage'))


# Create a state token to prefent request forgery
# Store it in the session for later validation
@app.route('/login', methods=['GET', 'POST'])
def showLogin():
    if request.method == 'GET':
        state = ''.join(
                    random.choice(
                        string.ascii_uppercase + string.digits
                    ) for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state, cid=CLIENT_ID)
    return redirect(url_for('homePage'))


# Generic Disconnect (multiple providers)
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        print "Disconnecting from provider: %s" % login_session['provider']
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
    login_session.pop('username', None)
    login_session.pop('email', None)
    login_session.pop('picture', None)
    login_session.pop('user_id', None)
    login_session.pop('provider', None)
    logout_user()
    print "Disconnect: User logged out"
    flash("You have successfully been logged out")
    return redirect(url_for('homePage'))


# Helpers for User ops:
def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(username=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Required for login_manager
@login_manager.user_loader
def user_loader(user_id):
    return session.query(User).filter_by(id=user_id).first()


if __name__ == '__main__':
    app.secret_key = json.loads(
                        open('g_auth.json', 'r')
                        .read())['web']['client_secret']
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
