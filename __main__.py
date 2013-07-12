#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import the Redmine class
from redmine import Redmine
from dateutil.relativedelta import relativedelta
import time
from urllib2 import HTTPError
import unicodedata, re

control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))

def onlyPrintable(s):
	return control_char_re.sub('', s)

def toTimestamp(t):
	return int(time.mktime(t.timetuple()))

def formatIssueLog(issue, directory, date, action):
	return "|".join([str(toTimestamp(date)), issue.author.login or issue.author.name or "Unknown", action, onlyPrintable(directory or '') + '/' + onlyPrintable(issue.subject or "No subject").replace('\\','_').replace('/', '_')])

def formatCreationLog(issue, directory, date):
	return formatIssueLog(issue, directory, date, 'A')

def formatModifyLog(issue, directory, date):
	return formatIssueLog(issue, directory, date, 'M')

def formatDeletionLog(issue, directory, date):
	return formatIssueLog(issue, directory, date, 'D')


eventList = []
server = Redmine('http://dev.w42.ru', key = api_key)
projects = server.projects(key = api_key)
#['speek', 'qt-dev']

filter_date = time.strptime("2013-07-01", "%Y-%m-%d")
issues_filter = ">=" + time.strftime("%Y-%m-%d", filter_date)
for project in projects:
	projectName = project.name
	# project = server.projects[projectName]
	# Find Eric in the user data
	# Extend issues in project assigned to user by two weeks
	#assigned_to_id=user.id):
	
	#print "Созданы:", issues_filter, int(time.mktime(filter_date))
	try:
		for issue in project.issues(status_id="*", created_on=issues_filter, sort="created_on", subproject_id='!*'):
			event_date = issue.created_on
			eventList.append( (event_date, formatCreationLog(issue, projectName, event_date)) )
		#print "Обновлены:", issues_filter
		for issue in project.issues(status_id="open", updated_on=issues_filter, sort="updated_on", subproject_id='!*'):
			event_date = issue.updated_on
			eventList.append( (event_date, formatModifyLog(issue, projectName, event_date)) )
		for issue in project.issues(status_id="closed", updated_on=issues_filter, sort="updated_on", subproject_id='!*'):
			event_date = issue.updated_on
			eventList.append( (event_date, formatDeletionLog(issue, projectName, event_date)) )
	except:
		pass
	# except HTTPError as e:
	# 	if e.code != 403:
	# 		raise
	
eventList.sort()
for message in eventList:
	print message[1].encode('utf-8')

