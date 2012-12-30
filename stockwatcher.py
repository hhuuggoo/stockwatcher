import requests
import datetime as dt
import math

def get_prices(stocks):
    format_url = "http://finance.yahoo.com/d/quotes.csv?s=%s&f=l1"
    stock_string = ",".join(stocks)
    url = format_url % stock_string
    prices = [float(x) for x in requests.get(url).content.split()]
    price_dict = dict(zip(stocks, prices))
    return price_dict


    
def run(stocks, thresholds, interval, alltimes, notify,
        lastprices=None, lasttime=None, loop=False, newprices=None):
    """
    stocks : list of strings
    thresholds : list or floats(percentage thresholds)
    interval : polling interval
    alltimes : times where we want all prices sent
    notify : callback for notification, takes pricedict as args, and
        list of stocks that have exceed some threshold
    lastprices : optional, lastprices we were notified at.  used for
        calculating thresholds
    lasttime : optional, lasttime we polled (shd be python datetime)
    """
    if lastprices is None:
        lastprices = {}
    if newprices is None:
        price_dict = get_prices(stocks)
    else:
        price_dict = newprices
    currtime = dt.datetime.now().time()
    if lasttime is None:
        notify(price_dict, [])
        lastprices.update(price_dict)
    elif any([lasttime.time() < x and currtime >= x for x in alltimes]):
        notify(price_dict, [])
        lastprices.update(price_dict)        
    else:
        tonotify = {}
        for stock, threshold in zip(stocks, thresholds):
            lastprice = lastprices.get(stock)
            currprice = price_dict.get(stock)
            if lastprice is None or \
                   abs(math.log(lastprice/currprice)) >= threshold:
                tonotify[stock] = currprice
        if len(tonotify) > 0:
            notify(price_dict, tonotify.keys())
            lastprices.update(tonotify)
    if loop:
        time.sleep(interval)
        run(stocks, thresholds, interval, alltimes, notify,
            lastprices=lastprices, lasttime=currtime)

if __name__ == "__main__":
    pass
