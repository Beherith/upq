import urllib
import gzip
import urlparse
import os.path

from upqjob import UpqJob
from upqdb import UpqDB

class Rapidsync(UpqJob):
	def run(self):
		repos=self.fetchListing(self.getcfg('mainrepo', "http://repos.caspring.org/repos.gz"))
		i=0
		for repo in repos:
			sdps=self.fetchListing(repo[1] + "/versions.gz")
			for sdp in sdps:
				"""
				values = {
						"tag"=sdp[0],
						"md5"=sdp[1],
						"depends"=sdp[2],
						"name"=sdp[3],
				}
				"""
				res=UpqDB().query("SELECT * FROM springdata_archives WHERE BINARY name='%s'" % (sdp[3]))
				row=res.first()
				if row: #is already known
					values["fid"] = row['fid']
					#check if sdp is set, if not update
					if len(row['sdp'])<=0:
						#delete tag from existing files
						UpqDB().query("UPDATE springdata_archives SET tag=NULL WHERE tag='%s'", (sdp[0]))
						UpqDB().query("UPDATE springdata_archives SET tag='%s', sdp='%s' WHERE fid='%s'" % (sdp[0], repo[1] +"packages/" + sdp[1], row['fid']))
				else:
					#TODO: add somehow to db without fid (download by rapid + create it?)
					if i<5: #limit output
						self.logger.debug("file isn't avaiable as .sdz but as .sdp: %s %s %s" % (sdp[1], sdp[0], sdp[3]))
						i=i+1
	def fetchListing(self, url):
		self.logger.debug("Fetching %s" % (url))
		ParseResult=urlparse.urlparse(url)
		dir=os.path.join(self.getcfg('temppath', '/tmp'), ParseResult.hostname)
		filename=os.path.basename(ParseResult.path)
		absname=os.path.join(dir, filename)
		if not os.path.exists(dir):
			os.makedirs(dir)
		urllib.urlretrieve(url,absname)
		gz = gzip.open(absname)
		lines=gz.readlines()
		gz.close()
		res=[]
		for line in lines:
			res.append(line.split(","))
		return res

