from chime.client.naas import NaaSApi
from chime.client.pgw import PGWApi
from chime.client.xpaas import XPaaSApi
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


# Configure CHIME Services endpoints
NAAS_URL = 'http://10.72.8.21:9091/naas' # 'https://apim.chime-dev.cellwize.com/gateway/naas'
XPAAS_URL = 'http://10.72.8.78:9092/xpaas'
PGW_URL = 'http://10.72.8.78:9093/pgw'
AUTH_URL = 'https://am.chime-dev.cellwize.com/gateway/chime/oauth/token'

# Configure Client_Id and Client_Secret to enable authentication
CLIENT_ID = "SZc5nxWR2HNT3zL6xr8xIn7S1bQ"
CLIENT_SECRET = "ChXh2d1AvLqYDfcQopBRFq72D1k"

HEADERS = {}

'''
# CHIME uses Oauth2 client credentials authentication flow
if CLIENT_ID is not None and CLIENT_SECRET is not None:
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=AUTH_URL, client_id=CLIENT_ID,
                              client_secret=CLIENT_SECRET, verify=True)

    # init API client headers with access_token
    HEADERS = {'Authorization': 'Bearer ' + token.get('access_token')}
'''

# Init  clients
naas = NaaSApi(api_root_url=NAAS_URL, timeout=60, headers=HEADERS)
xpaas = XPaaSApi(api_root_url=XPAAS_URL, timeout=60, headers=HEADERS)
pgw = PGWApi(api_root_url=PGW_URL, timeout=60, headers=HEADERS)
