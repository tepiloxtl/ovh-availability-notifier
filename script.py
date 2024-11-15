import requests, json, time, pprint

endpoint = "https://eu.api.ovh.com/v1"
listurl = "/order/catalog/public/eco?ovhSubsidiary="
checkurl = "/dedicated/server/datacenter/availabilities?planCode="
country = "PL"

offerlistjson = requests.get(endpoint + listurl + country).json()
offerlist = {}
currentoffers = {}
changedoffers = {}

destinations = [{"type": "discord",
                  "url": "your webhook here",
                  "sku": ["24ska01"]},
                {"type": "ntfy",
                  "url": "your webhook here",
                 "auth": "your Basic or Bearer token",
                  "sku": ["24ska01"]}]

# https://healthchecks.io/, skipped if empty or None
healthcheck = ""

# , ["24skgame01-sgp", "24skgame01-sgp.ram-32g-noecc-2133.hybridsoftraid-2x450nvme-1x4000sa"]

def notify_discord(destination, offername, offer):
    data = {"username": "OVH Eco checker"}
    avl = ""
    color = "15548997"
    for av in offer:
        avl = avl + av + ": " + offer[av] + "\n"
        if offer[av] != "unavailable":
            color = "5763719"
    #print(avl)
    data["embeds"] = [{'title': offerlist[offername]['invoiceName'], 'description': offerlist[offername]["price"], 'color': color, 'footer': {'text': ''}, 'author': {'name': 'OVH Eco checker'}, 'fields': [{'name': 'availability:', 'value': avl, 'inline': True}]}]
    swh = requests.post(destination["url"], json=data)
    #print(swh.text)

def notify_ntfy(destination, offername, offer):
    tags = "x"
    avl = ""
    for av in offer:
        avl = avl + av + ": " + offer[av] + "\n"
        if offer[av] != "unavailable":
            tags = "white_check_mark"
    tags = tags + "," + offername
    #print(avl)
    requests.post(destination["url"],
        data=avl,
        headers={
            "Title": offerlist[offername]['invoiceName'] + " availability",
            "Priority": "urgent",
            "Tags": tags,
            "Authorization": destination["auth"]
        })


currency = offerlistjson["locale"]["currencyCode"]

for item in offerlistjson["plans"]:
    price = None
    for item2 in item["pricings"]:
        if item2["phase"] == 1 and item2["mode"] == "default":
            price = str(item2["price"] / 100000000) + currency
    planCode = item["planCode"]
    invoiceName = item["invoiceName"]
    try:
        range = item["blobs"]["commercial"]["range"]
    except:
        range = str(None)
    offerlist[planCode] = {"invoiceName": invoiceName, "range": range, "price": price}

pprint.pprint(offerlist)

tocheck = []
for destination in destinations:
    for item in destination["sku"]:
        if item not in tocheck:
            tocheck.append(item)

# 120H┃1440H┃1H-high┃1H-low┃2160H┃240H┃24H┃480H┃720H┃72H┃comingSoon┃unavailable┃unknown

while True:
    for item in tocheck:
        temp = {}
        if item not in currentoffers:
            currentoffers[item] = {}
        offer = requests.get(endpoint + checkurl + item).json()
        for item2 in offer[0]["datacenters"]:
            temp[item2["datacenter"]] = item2["availability"]
        if currentoffers[item] != temp:
            currentoffers[item] = temp
            changedoffers[item] = currentoffers[item]

    for destination in destinations:
        for offer in destination["sku"]:
            if offer in changedoffers:
                if destination["type"] == "discord":
                    notify_discord(destination, offer, changedoffers[offer])
                elif destination["type"] == "ntfy":
                    notify_ntfy(destination, offer, changedoffers[offer])


    changedoffers = {}
    if healthcheck:
        requests.post(healthcheck)
    time.sleep(60)