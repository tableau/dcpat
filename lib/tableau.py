import requests


class TableauClient:
    def __init__(self, server: str, site_name: str, token_prefix: str):
        self.server = server
        self.site_name = site_name
        self.token_prefix = token_prefix
        self.session_token = None
        self.site_id = None

    def sign_in(self, token_name, token_value):
        url = f"{self.server}/api/3.15/auth/signin"
        headers = {
            'Accept': 'application/json',
        }
        body = {
            "credentials": {
                "personalAccessTokenName": token_name,
                "personalAccessTokenSecret": token_value,
                "site": {
                    "contentUrl": self.site_name
                }
            }
        }
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        content = response.json()
        self.session_token = content['credentials']['token']
        self.site_id = content['credentials']['site']['id']
        return content

    def sign_out(self):
        url = f"{self.server}/api/3.15/auth/signout"
        headers = {
            'Accept': 'application/json',
            'x-tableau-auth': self.session_token,
        }
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        self.session_token = None
        self.site_id = None
