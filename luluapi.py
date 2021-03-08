import base64
import logging
import requests


# create logger with 'spam_application'
logger = logging.getLogger('luluapi')
logger.setLevel(logging.DEBUG)




# CONSTANTS
################################################################################
BASE_URL = "https://api.lulu.com/"
SANDBOX_BASE_URL = "https://api.sandbox.lulu.com/"





# CLIENT
################################################################################

class LuluApiClient(object):
    """
    Helper class whose methods allow access to Studo API endpoints for reports,
    corrections, and other automation.
    """

    def __init__(self, client_key=None, client_secret=None, base_url=BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.client_key = client_key
        self.client_secret = client_secret
        self.bearer_token = None
        if self.client_key and self.client_secret:
            self.bearer_token = self._get_bearer_token(
                client_key=self.client_key,
                client_secret=self.client_secret
            )

    def _get_bearer_token(self, client_key=None, client_secret=None):
        TOKEN_ENDPOINT = self.base_url + "/auth/realms/glasstree/protocol/openid-connect/token"
        post_data = {
            "grant_type": "client_credentials",
        }
        combined = client_key + ":" + client_secret
        combined_bytes = combined.encode('ascii')
        combined_base64 = base64.b64encode(combined_bytes)
        headers = {
            "Authorization": "Basic " + combined_base64.decode('ascii')
        }
        response = requests.post(TOKEN_ENDPOINT, data=post_data, headers=headers)
        json_data = response.json()
        logging.debug("Obtained access_token=" + json_data["access_token"])
        return json_data["access_token"]


    def get_print_jobs(self):
        PRINTJOBS_ENDPOINT = self.base_url + "/print-jobs/"
        headers = {
            'Cache-Control': 'no-cache',
            'Authorization': 'Bearer ' + self.bearer_token, 
        }
        response = requests.get(PRINTJOBS_ENDPOINT, headers=headers)
        assert response.status_code == 200, 'GET /print-jobs/ failed'
        return response.json()['results']



# UTILS
################################################################################

def check_creds(creds):
    """
    Check if "Basic b64encode({client_key}:{client_secret})" == combined_base64.
    Raises if the creds["combined_base64"] doesn't match the key and secret.
    """
    combined = creds["client_key"] + ":" + creds["client_secret"]
    combined_bytes = combined.encode('ascii')
    expected = base64.b64encode(combined_bytes)
    observed = creds['combined_base64']
    assert expected == observed

