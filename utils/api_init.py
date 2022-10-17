from chime.client.naas import NaaSApi
from chime.client.pgw import PGWApi
from chime.client.xpaas import XPaaSApi
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from . import context, logger_config
import os


# Configure CHIME Services endpoints
NAAS_URL = context.context.get('NaaS_IP')
XPAAS_URL = context.context.get('XPaaS_IP')
PGW_URL = context.context.get('PGW_IP')
AUTH_URL = context.context.get('Auth_IP')

logger_config.logger.info(f"NAAS_URL -> {NAAS_URL}")
logger_config.logger.info(f"XPAAS_URL -> {XPAAS_URL}")
logger_config.logger.info(f"PGW_URL -> {PGW_URL}")
logger_config.logger.info(f"AUTH_URL -> {AUTH_URL}")

# Configure Client_Id and Client_Secret to enable authentication
CLIENT_ID = None
CLIENT_SECRET = None
HEADERS = {}

if len(AUTH_URL) > 10:
    CLIENT_ID = context.context.get('CLIENT_ID')
    CLIENT_SECRET = context.context.get('CLIENT_SECRET')

    logger_config.logger.info(f"CLIENT_ID -> {CLIENT_ID[0:min(10, len(CLIENT_ID))]}...")
    logger_config.logger.info(f"CLIENT_SECRET -> {CLIENT_SECRET[0:min(10, len(CLIENT_SECRET))]}...")

    CERT_PATH = os.path.dirname(__file__) + '/STRootCA-SSLSubCA.pem'

    if len(CLIENT_ID) > 5 and len(CLIENT_SECRET) > 5:
        client = BackendApplicationClient(client_id=CLIENT_ID)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=AUTH_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, verify=CERT_PATH)

        # init API client headers with access_token
        HEADERS = {'Authorization': 'Bearer ' + token.get('access_token')}
        logger_config.logger.info(f"HEADERS filled")

    # Init  clients
    naas = NaaSApi(api_root_url=NAAS_URL, timeout=60, headers=HEADERS, ssl_verify=CERT_PATH)
    xpaas = XPaaSApi(api_root_url=XPAAS_URL, timeout=60, headers=HEADERS, ssl_verify=CERT_PATH)
    pgw = PGWApi(api_root_url=PGW_URL, timeout=60, headers=HEADERS, ssl_verify=CERT_PATH)

else:

    naas = NaaSApi(api_root_url=NAAS_URL, timeout=60, headers=HEADERS)
    xpaas = XPaaSApi(api_root_url=XPAAS_URL, timeout=60, headers=HEADERS)
    pgw = PGWApi(api_root_url=PGW_URL, timeout=60, headers=HEADERS)
