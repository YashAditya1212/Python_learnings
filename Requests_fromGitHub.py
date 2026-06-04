# requests module handles get requests
import http

import requests

response= requests.get("http://api.github.com/repos/yashaditya1212/Python_learnings")

print(response.json());
