#!C:\Users\Ronnie Mae\AppData\Local\Programs\Python\Python312\python.exe

import requests
import time
from bs4 import BeautifulSoup

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

def send_telegram_message(message):
    """Sends a message to the Telegram group."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def read_sites(file_path):
    """Reads sites from a file."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def write_to_file(file_path, data):
    """Writes data to a file."""
    with open(file_path, 'a') as file:
        file.write(data + '\n')

def check_site_status(url):
    """Check if the site is live."""
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def detect_payment_gateways(html):
    """Detect payment gateways in the site's HTML."""
    gateways = {
        "braintree": "braintree_credit_card",
        "adyen": "adyen_credit_card",
        "cybersource": "cybersource_secure",
        "shopify": "shopify_payments",
        "paypal": "paypal_express",
        "square": "square_credit_card",
        "authorize.net": "authorize_net_cim_credit_card",
        "worldpay": "worldpay_secure",
        "bluesnap": "bluesnap_card",
        "2checkout": "2checkout_payment",
        "amazon pay": "amazon_pay_gateway",
        "paytabs": "paytabs_secure",
        "wepay": "wepay_credit_card",
        "skrill": "skrill_wallet",
        "payoneer": "payoneer_transfer",
        "moneris": "moneris_secure"
    }
    detected = [(gateway, gateways[gateway]) for gateway in gateways if gateway in html.lower()]
    return detected if detected else [("NA", "NA")]

def detect_captcha(html):
    """Check if the site uses a captcha."""
    return '✅' if 'captcha' in html.lower() else '❌'

def detect_cloudflare(headers):
    """Check if the site uses Cloudflare."""
    return '✅' if 'cf-ray' in headers or 'cloudflare' in headers.get('server', '').lower() else '❌'

def detect_auth_gate(html):
    """Detect if the site has authentication gateway-related keywords."""
    return any(keyword in html.lower() for keyword in ['auth', 'gateway'])

def get_platform(html):
    """Detect the platform used by the site."""
    if 'shopify' in html.lower():
        return 'Shopify'
    elif 'woocommerce' in html.lower():
        return 'WooCommerce'
    elif 'magento' in html.lower():
        return 'Magento'
    else:
        return 'Unknown'

def get_server_info(headers):
    """Retrieve server information from headers."""
    return headers.get('server', 'Unknown')

def detect_vbv(html):
    """Check for VBV (Verified by Visa) indications in the HTML."""
    return '✅' if 'verified by visa' in html.lower() else '❌'

def process_sites(input_file, output_file):
    """Process sites and write results to output file."""
    sites = read_sites(input_file)
    for site in sites:
        if not site.startswith('http'):
            site = 'http://' + site
        print(f"Processing: {site}")

        if check_site_status(site):
            try:
                start_time = time.time()
                response = requests.get(site, timeout=10)
                elapsed_time = round(time.time() - start_time, 1)
                html = response.text
                headers = response.headers

                gateways = detect_payment_gateways(html)
                captcha = detect_captcha(html)
                cloudflare = detect_cloudflare(headers)
                auth_gate = detect_auth_gate(html)
                platform = get_platform(html)
                server_info = get_server_info(headers)
                vbv = detect_vbv(html)
                
                for gateway, gateway_type in gateways:
                    result = (f"{site} | {gateway} | {gateway_type} | Captcha: {captcha} | Cloudflare: {cloudflare} | "
                              f"Platform: {platform} | Server Info: {server_info} | Auth Gate: {auth_gate} | VBV: {vbv} | {elapsed_time}s")
                    print(result)
                    write_to_file(output_file, result)
                    send_telegram_message(result)
            
            except Exception as e:
                print(f"Error processing {site}: {e}")
        else:
            print(f"Site is dead: {site}")

if __name__ == "__main__":
    input_file = "sites.txt"  # Input file containing site URLs
    output_file = "hit.txt"   # Output file for live sites

    process_sites(input_file, output_file)

# Example Webhook
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Received webhook: {data}")
    return jsonify({"status": "success", "data": data}), 200

if __name__ == "__main__":
    app.run(port=5000)
