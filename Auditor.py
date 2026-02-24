import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import os

# CONFIGURATION
RISK_THRESHOLD = -0.05  # Alert if value drops > 5%
CHECK_INTERVAL = 15  # Seconds between audits
UNITS_HELD = 65  # Total units in our startup inventory


def get_live_market_price():

    try:
        url = "https://finance.yahoo.com/quote/GC=F"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        price_text = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'}).text
        return float(price_text.replace(',', ''))
    except Exception as e:
        print(f"Connection Error: {e}")
        return None


def run_audit(live_price):

    data = {
        'Batch_ID': [101, 102, 103, 104, 105],
        'Units': [10, 15, 8, 12, 20],
        'Acquisition_Cost': [live_price] * 5  # Simulate buying at the live price
    }
    df = pd.DataFrame(data)


    units = df['Units'].to_numpy()
    costs = df['Acquisition_Cost'].to_numpy()



    noise = np.random.uniform(-10, 10)
    simulated_price = live_price + noise


    total_cost = np.sum(units * costs)
    total_value = np.sum(units * simulated_price)
    pct_change = (total_value - total_cost) / total_cost

    return total_value, pct_change, simulated_price

def trigger_alert_system(total_value, pct_change):
    log_entry = pd.DataFrame([{
        'Timestamp': time.ctime(),
        'Value': total_value,
        'Change': pct_change,
        'Status': 'BREACH' if pct_change <= RISK_THRESHOLD else 'OK'
    }])

    log_entry.to_csv(
        'audit_history.csv',
        mode='a',
        index=False,
        header=not os.path.exists('audit_history.csv')
    )
# --- MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    print("... AI Auditor Active ...")
    print(f"Monitoring Market for {RISK_THRESHOLD * 100}% Margin Breach\n")

    try:
        for i in range(5):  # Run for 5 cycles
            real_price = get_live_market_price()

            if real_price:
                val, change, sim_p = run_audit(real_price)

                print(f"LOG [{time.strftime('%H:%M:%S')}] | Price: ${sim_p:,.2f} | Change: {change * 100:.4f}%")

                if change <= RISK_THRESHOLD:
                    print(" ALERT: CRITICAL MARGIN BREACH DETECTED!")
                else:
                    print(" Status: Healthy")
                trigger_alert_system(val, change)
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nAuditor stopped by user.")

    print("\nFinal Report: Audit stream finished.")

