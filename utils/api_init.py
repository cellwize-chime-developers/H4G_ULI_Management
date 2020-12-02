from chime.client.naas import NaaSApi
from chime.client.pgw import PGWApi
from chime.client.xpaas import XPaaSApi
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


# Configure CHIME Services endpoints
NAAS_URL = 'https://apim.chime-dev.cellwize.com/gateway/naas'
XPAAS_URL = 'https://apim.chime-dev.cellwize.com/gateway/xpaas'
PGW_URL = 'https://apim.chime-dev.cellwize.com/gateway/pgw'
AUTH_URL = 'https://am.chime-dev.cellwize.com/gateway/chime/oauth/token'

# Configure Client_Id and Client_Secret to enable authentication
CLIENT_ID = None
CLIENT_SECRET = None

HEADERS = {}

# CHIME uses Oauth2 client credentials authentication flow
if CLIENT_ID is not None and CLIENT_SECRET is not None:
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=AUTH_URL, client_id=CLIENT_ID,
                              client_secret=CLIENT_SECRET, verify=True)

    # init API client headers with access_token
    HEADERS = {'Authorization': 'Bearer ' + token.get('access_token')}

# Init  clients
naas = NaaSApi(api_root_url=NAAS_URL, timeout=60, headers=HEADERS)
xpaas = XPaaSApi(api_root_url=XPAAS_URL, timeout=60, headers=HEADERS)
pgw = PGWApi(api_root_url=PGW_URL, timeout=60, headers=HEADERS)
