
import requests
import time

class Client(object):
    api_base_path = "api/data/v9.1"
    default_header = {"Accept": "application/json, */*", "content-type": "application/json; charset=utf-8",
                      'OData-MaxVersion': '4.0', 'OData-Version': '4.0'}

    admin_consent_url = "https://login.microsoftonline.com/{0}/adminconsent"
    token_endpoint = "https://login.microsoftonline.com/{0}/oauth2/v2.0/token"

    def __init__(self, resource, client_id, client_secret, tenant_id="common", custom_scope=None):
        if not resource.endswith("/"):
            self.resource = resource + "/"
        else:
            self.resource = resource
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant = tenant_id
        self.custom_scope = custom_scope
        self.token = None
        self.token_expiration = 0
        self._service_doc = None

    def get_scope(self):
        if self.custom_scope is not None:
            return self.custom_scope
        return "{}.default".format(self.resource)

    def _renew_token(self):
        if self.token is None or time.time() > self.token_expiration:
            self.get_token()
        return self.token

    def get_headers(self, include_annotations=False):
        t = self._renew_token()
        h = {"Authorization": "Bearer " + t}
        h.update(self.default_header)
        if include_annotations:
            h["Prefer"] = 'odata.include-annotations="*"'
        return h

    def get_consent_url(self, tenant=None, redirect_url="https://login.microsoftonline.com/common/oauth2/nativeclient"):
        admin_base_url = self.admin_consent_url.format(self.tenant)
        admin_base_url = admin_base_url + "?client_id={0}&state=mystate&redirect_uri={1}".format(self.client_id, redirect_url)
        return admin_base_url

    def get_token(self):
        token_base_url = self.token_endpoint.format(self.tenant)
        res = requests.post(token_base_url, data={"client_id": self.client_id,
                                                  "client_secret": self.client_secret,
                                                  "scope": self.get_scope(),
                                                  "grant_type": "client_credentials"})
        if res.status_code >= 400:
            raise RuntimeError("Error {0} from API: {1}".format(res.status_code, res.text))

        d = res.json()
        expires_in = d["expires_in"]
        token = d["access_token"]
        self.token = token
        self.token_expiration = (time.time() + expires_in) - 10
        return token

    def make_request(self, method, endpoint):
        url = "{0}{1}/{2}".format(self.resource, self.api_base_path, endpoint)
        return self._make_request(method, url)

    def _raise_on_error(self, res):
        if res.status_code >= 400:
            error_text = res.text
            if error_text and len(error_text) > 1:
                error_text = error_text[250]
            else:
                error_text = "Unknown"
            raise RuntimeError("Error {0}({1}) from API: {2}".format(res.status_code, res.url, res.text))

    def _make_request(self, method, url, include_annotations=False):
        h = self.get_headers(include_annotations=include_annotations)
        res = requests.request(method, url, headers=h)
        self._raise_on_error(res)
        return res.json()

    def download_metadata(self, filename):
        url = "{0}{1}/$metadata".format(self.resource, self.api_base_path)
        t = self._renew_token()
        h = {"Authorization": "Bearer " + t}
        res = requests.get(url, headers=h)
        self._raise_on_error(res)
        with open(filename, "wb") as outfile:
            outfile.write(res.content)

    def whoami(self):
        return self.make_request("get", "WhoAmI")

    def get_something(self):
        return self.make_request("get", "accounts?$top=2")

    @property
    def service_doc(self):
        if self._service_doc is None:
            self._service_doc = self.make_request("get", "")
        return self._service_doc
