import requests
import posts
import json

url = "http://localhost:8080/decrypt"
key = '1010101010101010'
data = "ZFS5Pn6wJ6P7gKLA6ynl0w=="

#payload = {'key': key,'data': data}
#r = requests.post( url, data = payload)
#print(r.status_code)

x =  posts.doPost(url, key, data)
y = eval(x.text)
print y['data']
