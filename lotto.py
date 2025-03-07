
import http.client

conn = http.client.HTTPSConnection("florida-lottery-scratch-off-tickets-data.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "c817053327msh4d9149ae65dbfdbp1091d6jsn3bdf8a03f549",
    'x-rapidapi-host': "florida-lottery-scratch-off-tickets-data.p.rapidapi.com"
}

conn.request("GET", "/.app", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
