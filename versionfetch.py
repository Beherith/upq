#!/usr/bin/env python3

# This file is part of the "upq" program used on springfiles.springrts.com to manage file
# uploads, mirror distribution etc. It is published under the GPLv3.
#
#Copyright (C) 2011 Matthias Ableitner (spring #at# abma #dot# de)
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

# sf-sync: syncs file data with springfiles
# can be either initiaded by an updated file
# or maybe by the xml-rpc interface (or cron?)

from lib import log, upqconfig, upqdb

import sys
import json
import os


upqconfig.UpqConfig()
upqconfig.UpqConfig().readConfig()
db = upqdb.UpqDB()
db.connect(upqconfig.UpqConfig().db['url'], upqconfig.UpqConfig().db['debug'])

from jobs import versionfetch
j = versionfetch.Versionfetch("versionfetch", {})
j.run()
