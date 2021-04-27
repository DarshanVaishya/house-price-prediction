import requests
import os
from bs4 import BeautifulSoup

URL = "https://www.makaan.com/ahmedabad-residential-property/buy-property-in-ahmedabad-city?page="
headers = {
    "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    }

if os.path.isfile('static/data.csv'):
    os.system('cp static/data.csv static/old_data.csv')

f = open("static/data.csv", "w")
f.write("area,type,BHK,sqft,price,unit\n")

for i in range(1, 600):
    site = requests.get(URL + str(i), headers=headers)
    data = BeautifulSoup(site.content, 'html.parser')
    print("#" * 10, "Page " + str(i))
    j = 1

    for box in data.find_all('div', {'class' : 'infoWrap'}):
        try:
            BHK = (box.find('div', {'class' : 'title-line'})
                    .a.strong.span.text).strip()
            house_type = (box.find('div', {'class' : 'title-line'})
                    .a.strong.find_all('span')[2].text)
            area = box.find('span', {'itemprop' : 'addressLocality'}).strong.text
            highlight = box.find('table', {'class' : 'listing-highlights'})
            price = highlight.find('div', {'data-type' : 'price-link'}).span.text.strip()
            unit = highlight.find('span', {'class' : 'unit'}).text.strip()
            sqft = highlight.tbody.find_all('span')[2].text.strip()

            # print("Area: {}\nBHK: {}\nType: {}\nPrice: {}\nSqft: {}\n\n".format(area, BHK, house_type, price + unit, sqft))
            text = "{},{},{},{},{},{}\n".format(area,house_type,BHK,sqft,price,unit)
            print(j, text)
            f.write(text)

            j = j+1
        except:
            continue
