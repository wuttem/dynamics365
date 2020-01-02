# Dynamics365

Python Dynamics 365 API Client


## Usage

Create Application in Azure Active Directory
 - Use Native Application
 - Use "https://login.microsoftonline.com/common/oauth2/nativeclient" as redirect
 - Generate Client Secret
 - Get Application ID and Tenant ID (from Azure)

Create Application User in Dynamics CRM
 - with Application ID from above
 - generate User Role and assign to this user

```python
from dynamics365 import Client

crm_url = "https://SOMEONE.api.crm.dynamics.com/"
tenant_id = "TENANT_ID"
client_id = "CLIENT_ID (application)"
client_secret = "CLIENT_SECRET"

c = Client(crm_url, client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)

pprint(c.whoami())
```

## Build

Build Distribution and Uplaod to PIP

```bash
python setup.py sdist
twine upload dist/*
```