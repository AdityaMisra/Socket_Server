# Hacky way to import from parent directory
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import server_manager
exec(open(os.path.join(parentdir, "server_manager.py")).read())
con.host()
