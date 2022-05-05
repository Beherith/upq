import upqconfig, upqdb
import sys
cfg = upqconfig.UpqConfig()
cfg.readConfig()

from jobs import extract_metadata

db = upqdb.UpqDB()
db.connect(upqconfig.UpqConfig().db['url'], upqconfig.UpqConfig().db['debug'])

jobdata = {
	"file": sys.argv[1]
}
j = extract_metadata.Extract_metadata("extract_metadata", jobdata)
j.run()
