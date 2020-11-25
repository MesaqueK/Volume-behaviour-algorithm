from flask import Flask, render_template, request
import fxcmpy 
import config, json, requests
from socketIO_client import SocketIO

con = fxcmpy.fxcmpy(config_file='fxcm.cfg', server='demo')

TRADING_API_URL = 'https://api-demo.fxcm.com:443'
WEBSOCKET_PORT = 443
ACCESS_TOKEN = 'ed33f2881cd0fe40954e45910761437837ce2b9d'

app = Flask(__name__)

def on_connect():
    print('Websocket Connected: ' + socketIO._engineIO_session.id)

def on_close():
        print('Websocket Closed.')

socketIO =  SocketIO(TRADING_API_URL, WEBSOCKET_PORT, params={'access_token' : ACCESS_TOKEN})

socketIO.on('connect', on_connect)
socketIO.on('disconnect', on_close)

bearer_access_token = "Bearer " + socketIO._engineIO_session.id + ACCESS_TOKEN

print(bearer_access_token)

@app.route('/')
def dashboard():
    orders = fxcmpy.fxcmpy_oco_order
        
    return render_template('dashboard.html', alpaca_orders=orders)

@app.route('/webhook', methods=['POST'])
def webhook():
    webhook_message = json.loads(request.data)

    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }
    
    price = webhook_message['strategy']['order_price']
    amount = webhook_message['strategy']['order_contracts']
    symbol = webhook_message['ticker']
    side = webhook_message['strategy']['order_action']

    ordersell = con.create_market_sell_order(symbol, amount, side)
    orderbuy = con.create_market_buy_order(symbol, amount, side)
    
    return webhook_message