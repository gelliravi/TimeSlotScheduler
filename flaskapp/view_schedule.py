# coding=UTF-8
"""
View The Schedule
~~~~~~~~~~~~~~~~~

:Copyright © 2011 Mark Harviston <infinull@gmail.com>

 * Display course information in a convenient spreadsheet-like format
 * Upload a CSV formatted banweb style and upload it
 * TODO make PrefType proof

"""

import csv, operator, datetime

import flask
from flask import session, request, url_for, redirect, abort, flash, make_response, send_file

from flaskext.genshi import render_response
from flaskapp.globals import *

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from database import db_session as sess
from datamodel import Schedule, PrefType
from StringIO import StringIO

@app.route('/view_schedule')
def view_schedule():
	schedule = sess.query(Schedule).one()
	assignments = schedule.assignments

	schedule = sess.query(Schedule).one()

	errors = []
	for assn in schedule.assignments:
		if assn.course is None:
			errors.append('%r missing course' % assn)

		if assn.mentor is None:
			errors.append('%r missing mentor' % assn)

		if assn.assn_id is None:
			errors.append('%r missing id' % assn)

	if errors:
		raise Exception('%r' % errors)

	#Calculate statistics
	total_cost = sum(map(lambda x: x.cost, assignments))
	avg_cost = total_cost/len(assignments)

	return render_response('view_schedule.html', locals())

@app.route('/schedule.csv')
def view_schedule_as_csv():
	#TODO not sure if this is the best way to do it, seems like the output buffer could be opened directly, or something
	w_file = StringIO()
	gen_csv(w_file)
	w_file.seek(0) #rewind to beginning
	#return send_file(w_file, 'text/csv', as_attachment=False, attachment_filename='schedule.csv')
	return send_file(w_file, 'text/plain')

def gen_csv(w_file):
	schedule = sess.query(Schedule).one()
	assignments = schedule.assignments
	pref_types = sess.query(PrefType).all()

	#Calculate statistics
	total_cost = sum(map(lambda x: x.cost, assignments))
	avg_cost = total_cost/len(assignments)

	writer = csv.writer(w_file)

	pref_names = []
	for pref_type in pref_types:
		pref_names.append(pref_type.name + " Weight Cost")
		pref_names.append(pref_type.name + " Weight Index")

	writer.writerow(('CRN','Time','Theme','Faculty','Mentor','Cost')+pref_names)

	for assn in assignments:
		prefs = assn.course.prefs_as_dict()
		extra_cols = []
		for pref_type in pref_types:
			choice = assn.mentor.getChoiceByType(pref_type)

			if choice:
				weight_num = str(choice.weight.weight_num)
				weight_val = '%.2f' % choice.weight.weight_val
			else:
				weight_num = 'N/A'
				weight_val = 0

			extra_cols.append(weight_val)
			extra_cols.append(weight_num)

		writer.writerow((
			assn.course.crn,
			prefs['Time'],
			prefs['Theme'],
			prefs['Faculty'],
			assn.mentor.full_name,
			'%.2f' % assn.cost
		) + extra_cols)

	writer.writerow([])
	writer.writerow(('Total Cost', total_cost))
	writer.writerow(('Average Cost', avg_cost))
