import requests
import datetime as dt
import math
import time

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
    while True:
        if lastprices is None:
            lastprices = {}
        if newprices is None:
            price_dict = get_prices(stocks)
        else:
            price_dict = newprices
        currdt = dt.datetime.now()
        currtime = currdt.time()
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
            print "loopcheck", price_dict, lastprices
            if len(tonotify) > 0:
                notify(price_dict, tonotify.keys())
                lastprices.update(tonotify)
        if not loop:
            break
        else:
            time.sleep(interval)
            lasttime=currdt

if __name__ == "__main__":
    def ses_notify(pricedict, stocks):
        print "notify", pricedict, stocks
        lines = []
        keys = pricedict.keys()
        keys.sort()
        if stocks:
            lines.append("big movers, %s" % ",".join(stocks))
        for k in keys:
            v = pricedict[k]
            lines.append("%s : %.2f" % (k,v))
        message = "\n".join(lines)
        print message
        import json
        with open("/home/yata/keys.json") as f:
            data = f.read()
            keys = json.loads(data)
        from boto.ses import SESConnection
        connection = SESConnection(
            aws_access_key_id=keys["AWS_ACCESS_KEY"],
            aws_secret_access_key=keys["AWS_SECRET_KEY"]
            )
        connection.send_email("info@eff.iciently.com",
                              "stock update", message,
                              ["humongo.shi@gmail.com", "wendy.tng@gmail.com"],
                              )

    stocks = ["IVV", "VXX", "AAPL", "GOOG", "EMB", "EEM", "FXI", "TIP", "HYG", "PGF"]
    thresholds = [0.005, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.005, 0.01, 0.01]
    lastprices = get_prices(stocks)
    run(stocks, thresholds, 60.0, [dt.time(9,45), dt.time(16,45)],
        ses_notify, loop=True, lasttime=None, lastprices=lastprices)
    
    



