# Hacky way to import from parent directory
import os
import sys
import inspect
from server_manager import con


current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


exec(open(os.path.join(parent_dir, "server_manager.py")).read())
con.connect(con.search()[0].address)
