import stockwatcher
import datetime as dt

def test_get_prices():
    result = stockwatcher.get_prices(['IVV', 'BRCM', 'SPY'])
    assert len(result) == 3
def test_run():
    dummyprices = {'IVV':100.0, 'BRCM' : 200.0, "SPY" : 300.0}
    dummyprices2 = {'IVV':103.0, 'BRCM' : 200.0, "SPY" : 140.0}    
    result = []
    def notify_callback(prices, hotstocks):
        result.append((prices, hotstocks))
    currtime = dt.datetime.now()
    fakecurrtime =  (currtime - dt.timedelta(minutes=1)).time()
    stockwatcher.run(['IVV', 'BRCM', 'SPY'],
                     [0.01, 0.05, 0.01],
                     1.0,
                     [(currtime - dt.timedelta(minutes=1)).time()],
                     notify_callback,
                     lasttime=currtime - dt.timedelta(minutes=2),
                     loop=False,
                     newprices=dummyprices
                     )
    assert len(result[0][0]) == 3 and len(result[0][1]) == 0
    result = []
    stockwatcher.run(['IVV', 'BRCM', 'SPY'],
                     [0.01, 0.05, 0.01],
                     1.0,
                     [(currtime - dt.timedelta(minutes=1)).time()],
                     notify_callback,
                     lasttime=currtime - dt.timedelta(seconds=30),
                     loop=False,
                     newprices=dummyprices,
                     lastprices=dummyprices
                     )
    assert len(result) == 0
    result = []
    stockwatcher.run(['IVV', 'BRCM', 'SPY'],
                     [0.01, 0.05, 0.01],
                     1.0,
                     [(currtime - dt.timedelta(minutes=1)).time()],
                     notify_callback,
                     lasttime=currtime - dt.timedelta(seconds=30),
                     loop=False,
                     newprices=dummyprices2,
                     lastprices=dummyprices
                     )
    assert len(result) == 1
    assert 'IVV' in result[0][1]
    assert 'SPY' in result[0][1]
    assert 'BRCM' not in result[0][1]        

    
    
