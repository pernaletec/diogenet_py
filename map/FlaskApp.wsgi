import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/map/")

from index import server as application