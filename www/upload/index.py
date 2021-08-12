#!/usr/bin/python3

import cgi, os, cgitb, html, sys

print("Content-type: text/html\n")
cgitb.enable()

if os.environ.get('UPQ_DIR'):
	sys.path.insert(0, os.environ.get('UPQ_DIR'))

upq_creds = {}
credentials = os.environ.get('UPQ_CREDENTIALS')
if credentials:
	for user_pass in credentials.split(';'):
		user, passwd = user_pass.split(',')
		upq_creds[user] = passwd

def ShowForm(tplvars):
	with open("form.html", "r") as f:
		content = f.read()
	for k, v in tplvars.items():
		content = content.replace("%" + k + "%", v)
	print(content)


def save_uploaded_file(fileitem, upload_dir):
	os.makedirs(upload_dir, exist_ok=True)

	filename = fileitem.filename.replace("/", "_")
	if not filename:
		return
	absfile = os.path.join(upload_dir, filename)
	with open(absfile, 'wb') as fout:
		while 1:
			chunk = fileitem.file.read(100000)
			if not chunk: break
			fout.write(chunk)
	return absfile

def CheckAuthInternal(username, password):
	for user, passwd in upq_creds.items():
		if user == username and passwd == passwd:
			return True 
	return False

def CheckAuth(username, password):
	if not username or not password:
		return False
	import xmlrpc.client
	proxy = xmlrpc.client.ServerProxy("https://springrts.com/api/uber/xmlrpc")
	res = proxy.get_account_info(username, password)
	return res["status"] == 0

def CheckFields(form, required):
	for k in required:
		if not k in form:
			return False
	return True

def SaveUploadedFile(form):
	if not CheckFields(form, ["filename", "username", "password"]):
		return "Missing formdata"
	username = form.getvalue("username")
	password = form.getvalue("password")

	auth_pass = False

	if upq_creds:
		auth_pass = CheckAuthInternal(username, password)
	else:
		auth_pass = CheckAuth(username, password)

	if not auth_pass:
		return "Invalid Username or Password"
	fileitem = form["filename"]
	if not fileitem.file:
		return "Missing file form"
	filename = save_uploaded_file(fileitem, "/tmp/springfiles-upload")
	if not filename:
		return "Couldn't store file"

	upqdir = os.environ.get('UPQ_JOBS') or "/home/upq/upq"
	assert(os.path.isdir(upqdir))
	oldcwd = os.getcwd()
	os.chdir(upqdir)
	import sys
	sys.path.append(upqdir)
	#print(upqdir)
	output =  ParseAndAddFile(filename)
	os.chdir(oldcwd)
	return output

def SetupLogger(job):
	from io import StringIO
	import logging
	job.log_stream = StringIO()
	logging.basicConfig(stream=job.log_stream)
	logging.getLogger("upq").addHandler(logging.StreamHandler(stream=job.log_stream))

def ParseAndAddFile(filename):
	import upqconfig, upqdb
	cfg = upqconfig.UpqConfig()
	cfg.readConfig()
	db = upqdb.UpqDB()
	db.connect(upqconfig.UpqConfig().db['url'], upqconfig.UpqConfig().db['debug'])

	from jobs import extract_metadata
	jobdata = {
		"file": filename,
	}
	#FIXME: parse and add to db/mirror using pyseccompa
	j = extract_metadata.Extract_metadata("extract_metadata", jobdata)
	SetupLogger(j)
	j.run()
	return j.log_stream.getvalue()


form = cgi.FieldStorage()

msgs = SaveUploadedFile(form)

ShowForm({"messages": "<pre>" + html.escape(msgs) + "</pre>"})

