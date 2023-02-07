import sys
import logging
logging.basicConfig(stream=sys.stderr)
ys.path.insert(0,"/var/www/diogenet_horus_private/")
from index import server as application