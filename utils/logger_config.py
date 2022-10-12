from utils.context import app_config
from utils.context import context
import logging
import sys


class TrackingIdFilter(logging.Filter):
    def filter(self, record):
        record.transaction_id = context.get('TRACKING_ID')
        return True


logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s [%(name)s] [%(transaction_id)s] [%(levelname)s] %(message)s')

logger = logging.getLogger(app_config['application']['meta']['name'])
logger.addFilter(TrackingIdFilter())
