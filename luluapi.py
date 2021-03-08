import base64
from datetime import datetime
import logging
import requests
from requests.models import HTTPError
from urllib.parse import urlencode


# create logger with 'spam_application'
logger = logging.getLogger('luluapi')
logger.setLevel(logging.DEBUG)




# CONSTANTS
################################################################################
BASE_URL = "https://api.lulu.com/"
SANDBOX_BASE_URL = "https://api.sandbox.lulu.com/"


pod_package_ids = {
    "softcover": "0550X0850BWSTDPB060UW444GXX",
    "hardcover": "??",
}




# CLIENT
################################################################################

class LuluApiClient(object):
    """
    Helper class whose methods allow access to Studo API endpoints for reports,
    corrections, and other automation.
    """

    def __init__(self, client_key=None, client_secret=None, contact_email=None, base_url=BASE_URL):
        """
        Initalizing an API client requires `client_key` and `client_secret` and
        optionally `contact_email` (required when create print jobs).
        Set `base_url` to `SANDBOX_BASE_URL` to use the sandbox API during dev.
        """
        self.base_url = base_url.rstrip('/')
        self.client_key = client_key
        self.client_secret = client_secret
        self.contact_email = contact_email if contact_email else "printops@your.org"
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


    def _is_authenticated(self, headers):
        """
        Make a test request to an authenticated endpoint to see if auth is good.
        """
        TEST_ENDPOINT = self.base_url + "/print-jobs/"  # used to test auth
        response = requests.get(TEST_ENDPOINT, headers=headers)
        if response.status_code == 200:
            return True
        elif response.status_code == 401:
            logger.debug("Got HTTP 401 expried auth token so have to renew it.")
            return False
        elif response.status_code == 403:
            raise HTTPError("Got HTTP 403 Unauthorized. Check credentials.")
        else:
            print("Response=", response.json())
            raise HTTPError("Unexpected HTTP code " + str(response.status_code))

    def get_headers(self, checkauth=True):
        headers = {
            'Cache-Control': 'no-cache',
            'Authorization': 'Bearer ' + self.bearer_token, 
        }
        if checkauth:
            if not self._is_authenticated(headers):
                logger.debug('Renewing bearer token...')
                self.bearer_token = self._get_bearer_token(
                    client_key=self.client_key,
                    client_secret=self.client_secret
                )
                headers["Authorization"] = 'Bearer ' + self.bearer_token
                if self._is_authenticated(headers):
                    logger.debug("...bearer token successfully renewed.")
                else:
                    raise HTTPError('Failed to renew auth token after 1 attempt')
        return headers


    def get_print_jobs(self):
        PRINTJOBS_ENDPOINT = self.base_url + "/print-jobs/"
        headers = self.get_headers()
        response = requests.get(PRINTJOBS_ENDPOINT, headers=headers)
        assert response.status_code == 200, 'GET /print-jobs/ failed'
        return response.json()['results']


    def create_print_job(self, address, books, shipping_level, external_id=None):
        PRINTJOBS_ENDPOINT = self.base_url + "/print-jobs/"

        if external_id is None:
            external_id = "printjob-" + datetime.now().strftime("%Y%m%d__%H%M")

        # Prepare line items from book order info in `books` list
        line_items = []
        for book in books:
            if "external_id" in book:
                item_external_id = book["external_id"]
            else:
                item_external_id = "item-" + datetime.now().strftime("%Y%m%d__%H%M")
            line_item = {
                "external_id": item_external_id,
                "printable_normalization": {
                    "cover": { "source_url": book["cover_source_url"] },
                    "interior": { "source_url": book["interior_source_url"] },
                    "pod_package_id": book["pod_package_id"],
                },
                "quantity": book["quantity"],
                "title": book["title"],
            }
            line_items.append(line_item)

        # POST data
        data = {
            "contact_email": self.contact_email,
            "external_id": external_id,
            "line_items": line_items,
            "production_delay": 30,
            "shipping_address": address,
            "shipping_level": shipping_level,
        }
        headers = self.get_headers()
        response = requests.post(PRINTJOBS_ENDPOINT, json=data, headers=headers)
        response_data = response.json()
        if response.status_code == 201:
            job_id = str(response_data["id"])
            print("Print job with id=" + job_id + " sucessfully created.")
            print("Go to  " + self.base_url + "/" + job_id + "  for payment.")
        else:
            logger.error('POST to /print-jobs/ failed:')
            print(response_data)
        return response_data


    def get_print_shipping_options(self, **params):
        SHIPPING_OPTIONS_ENDPOINT = self.base_url + "/print-shipping-options/"
        url = SHIPPING_OPTIONS_ENDPOINT
        if params:
            url += "?" + urlencode(params)
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        assert response.status_code == 200, 'GET /print-shipping-options/ failed'
        return response.json() # ['results']



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

