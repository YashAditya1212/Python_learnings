# first identify requirement
# identify module which will talk to api 
# convert into json to traverse easily
import requests

response= requests.get("https://api.github.com/repos/kubernetes/kubernetes/pulls")

details= response.json()
for i in range(len(details)):
  print(details[i]["user"]["login"])
