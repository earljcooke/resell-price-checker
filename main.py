import requests
from flask import Flask, render_template, request
from craigslist import CraigslistForSale
from scipy import stats
from bs4 import BeautifulSoup


def generate_ebay_search(searchString):
    words = searchString.split()
    s = ''

    for i in range(len(words)):
        if i != len(words) - 1:
            s = s + words[i] + '+'
        else:
            s = s + words[i]
    return s


def get_ebay_prices(searchString):
    search = generate_ebay_search(searchString)
    URL = 'https://www.ebay.ca/sch/i.html?_sacat=0&_nkw=' + search + '&_frs=1'

    headers = {
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 '
                      'Safari/537.36 '
    }

    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    price = soup.findAll("li", {"class": "lvprice"})

    ebayPrices = []
    for t in price:
        text = t.contents[1].text.strip()
        text = text.replace('Trending at', '')
        text = text.replace('C $', '')
        text = text.replace(',', '')
        try:
            ebayPrices.append(float(text))
        except ValueError:
            continue
    return ebayPrices


def generate_kijiji_search(searchString):
    words = searchString.split()
    s = ''
    for i in range(len(words)):
        if i != len(words) - 1:
            s = s + words[i] + '-'
        else:
            s = s + words[i]
    return s


def get_kijiji_prices(searchString):
    search = generate_kijiji_search(searchString)
    URL = 'https://www.kijiji.ca/b-greater-vancouver-area/' + search + '/k0l80003'

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    price = soup.findAll('div', {'class': 'price'})

    kijijiPrices = []
    for t in price:
        text = t.text.replace('\n', '')
        text = text.replace('$', '')
        text = text.replace(',', '')
        text = text.strip()
        try:
            kijijiPrices.append(float(text))
        except ValueError:
            continue
    return kijijiPrices


def generate_craig_search(searchinput):
    word = searchinput.split()

    vancouver = CraigslistForSale(site='vancouver', filters={'query': word})

    craigslist_price = []

    i = 0

    for result in vancouver.get_results(geotagged=True):

        search_output = result

        search_output['price'] = search_output["price"].replace("$", "")

        craigslist_price.append(float(search_output['price']))

        print(search_output)

        i = i + 1

        if i == 15:
            break

    return craigslist_price


app = Flask(__name__)


@app.route("/", methods=['GET'])
def form():
    return render_template("index.html")


@app.route("/results", methods=['POST'])
def results():
    searchString = request.form['search']

    ebay = get_ebay_prices(searchString)
    ebayStats = stats.describe(ebay)
    ebayMin = ebayStats.minmax[0]
    ebayMax = ebayStats.minmax[1]
    ebayMean = float("{0:.2f}".format(ebayStats.mean))
    kijiji = get_kijiji_prices(searchString)
    kijijiStats = stats.describe(kijiji)
    kijijiMin = kijijiStats.minmax[0]
    kijijiMax = kijijiStats.minmax[1]
    kijijiMean = float("{0:.2f}".format(kijijiStats.mean))
    craigsList = generate_craig_search(searchString)
    craigsListStats = stats.describe(craigsList)
    craigsListMin = craigsListStats.minmax[0]
    craigsListMax = craigsListStats.minmax[1]
    craigsListMean = float("{0:.2f}".format(craigsListStats.mean))

    data = [
        {
            "min": str(craigsListMin),
            "max": str(craigsListMax),
            "mean": str(craigsListMean)
        },
        {
            "min": str(kijijiMin),
            "max": str(kijijiMax),
            "mean": str(kijijiMean)
        },
        {
            "min": str(ebayMin),
            "max": str(ebayMax),
            "mean": str(ebayMean)
        }
    ]

    return render_template("results.html", data=data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
