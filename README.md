# lulu-api-client
Test client and automation for print on demand services at https://api.lulu.com


## Obtain API Key and Secret

1. Go to https://developers.lulu.com/user-profile/api-keys
   to obtain the client key, secret, and base64 encoded combined,
   and put the info into `credentials/production.json` imitating
   the JSON structure in `credentials/example.json`.  
2. For dev and testing, obtain the sandbox credentials from
   https://developers.sandbox.lulu.com/user-profile/api-keys
   and save them to `credentials/sandbox.json`.


## Usage

```python
import json
creds = json.load(open('credentials/sandbox.json'))  # load API key and secret


from luluapi import LuluApiClient
from luluapi import SANDBOX_BASE_URL
apiclient = LuluApiClient(
    client_key=creds["client_key"],
    client_secret=creds["client_secret"],
    base_url=SANDBOX_BASE_URL)
assert apiclient.bearer_token, "ERRROR: bearer_token missing."


book = {
   "external_id": "test-line-item",
   "title": "My Book",
   "cover_source_url": "<online URL where to get the PDF of book's one-piece cover>",
   "interior_source_url": "<online URL where to get the PDF of interior>",
   "pod_package_id": "0550X0850BWSTDPB060UW444GXX",
   "quantity": 1,
}
books = [book]  # a print job can include multiple books

address = {
   "name": "Hans Dampf",
   "street1": "Street address 1",
   "street2": "(optional) street address second line",
   "city": "L\u00fcbeck",
   "postcode": "PO1 3AX",
   "state_code": "",
   "country_code": "GB",
   "phone_number": "844-212-0689",
}


apiclient.create_print_job(address, books, shipping_level="GROUND", external_id="test-print-job")

apiclient.get_print_jobs()

```


## File uploads

```bash
fab upload_file:/Users/ivan/Projects/Minireference/content/archives/noBSmath/v54/lulu/noBSguideMath_v54_softcover.pdf,name="noBSmath_luluapi_testrpint_Mar8_interior.pdf"
```
