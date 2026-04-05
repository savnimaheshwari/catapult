import requests
import xml.etree.ElementTree as ET
import urllib.parse

query = urllib.parse.quote("Hurricane Harvey")
url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
print(url)
response = requests.get(url)
print(response.status_code)
root = ET.fromstring(response.content)
for item in root.findall('.//item')[:3]:
    print(item.find('title').text)
    print(item.find('pubDate').text)
    print(item.find('link').text)
