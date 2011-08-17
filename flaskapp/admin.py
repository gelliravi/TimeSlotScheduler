# coding=UTF-8
"""

Administrate the Survey
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright © 2011 Mark Harviston <infinull@gmail.com>

"""
import string, random

from flask import session, request, url_for, redirect, abort

from flaskext.genshi import render_response

#flatland form processing
from flatland import Form, String
from flatland.out.genshi import setup

from flaskapp import genshi, app
from flaskapp.globals import *

from database import db_session as sess
from datamodel import User

import cas

@app.route('/')
def home():

	username = cas.validate()
	if username is None:
		user_type = 'anon'
	else:
		user = sess.query(User).get(username)
		if user is None:
			abort(403)
			#user = User(username,user_type='user')
		user_type = user.user_type

	app.logger.debug('username = %r\n' % username)

	if '_cas_token' in session:
		app.logger.debug('_cas_token = %r' % session['_cas_token'])
	else:
		app.logger.debug('_cas_token not set')

	return render_response('home.html',context=dict(user_type=user_type))

@app.route('/admin/survey')
def admin():
	username = cas.validate()
	uername or abort(401)

	user = sess.query(User).get(username)
	user.user_type == 'admin' or abort(403)
	#if not cas.validate(): abort(401)
	return 'foobar'

