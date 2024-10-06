import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Function to simulate order dates
def datesO(n, lambd):
    T = np.random.poisson(lambd, n)
    D = np.cumsum(T)
    return D

# Function to determine the number of orders executed before a given date d
def beforeD(d, D):
    n = len(D)
    k = 0
    for i in range(n):
        if D[i] <= d:
            k += 1
        else:
            break
    return k

# Function to simulate ordered quantities or values (i.e., price)
def quantityO(n, lambd, d, m, sigma):
    D = datesO(n, lambd)
    k = beforeD(d, D)
    D = D[:k]
    Q = np.random.binomial(n * lambd, 1 - sigma**2 / m, k)
    Q = np.cumsum(Q)
    Q = np.round(Q)
    out = pd.DataFrame({'Date': D, 'Quantity': np.insert(np.diff(Q), 0, Q[0]), 'C_Quantity': Q})
    return out

# Function to provide a supply sequence based on the sales sequence
def SupplyA(delay, alpha, n, lambd, d, m, sigma):
    sales = quantityO(n, lambd, d, m, sigma)
    S1 = sales['Date'] - delay
    S2 = np.round(sales['Quantity'] * (1 + alpha))
    S3 = np.cumsum(S2)
    outsupply = pd.DataFrame({'S_Dates': S1, 'SC_Quantity': S3, 'Date': sales['Date'], 'QuantityOC': sales['C_Quantity']})
    return outsupply

# Stock Price Dynamics function
def StockPriceD(u_price, u_sale, benefit_rate, expences_F, delay_supply, stock_rate, order_n, order_f, due_date, order_q, order_fluc):
    supply = SupplyA(delay_supply, stock_rate, order_n, order_f, due_date, order_q, order_fluc)
    C = supply['SC_Quantity'] # Cumulative Supply Quantity
    S = supply['QuantityOC'] # Quantity Ordered
    n_D = len(C) # Number of Dates
    Date = supply['Date'][:n_D] # Dates
    
    stock_price = (expences_F * (1 + benefit_rate) - u_sale * S + u_price * C) / (C - S) # Stock Price Dynamics
    
    date_zero = np.where(stock_price <= 0)[0] # Find the dates when the stock price is zero
    if len(date_zero) > 0:
        date_zero = date_zero[0] # Get the first date when the stock price is zero
    else:
        date_zero = None # If there is no date when the stock price is zero, set it to None
        
    stock_price[stock_price <= 0] = 0 # Set the stock price to zero when it is negative
    
    # Calculate the Quantity Ordered and Cumulative Supply Quantity for plotting
    Q = np.insert(np.diff(S), 0, S.iloc[0]) 
    S_cum = np.insert(np.diff(C), 0, C.iloc[0])

    # Convert the result into a dictionary for JSON response
    data = {
        "dates": Date.tolist(),
        "stock_price": stock_price.tolist(),
        "quantity_ordered": Q.tolist(),
        "cumulative_supply": C.tolist(),
    }    
    return jsonify(data)


@app.route('/api/simulation', methods=['POST', 'OPTIONS'])
def run_simulation():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return '', 200  # Respond with 200 OK without doing anything else
    # Read parameters from the request JSON
    data = request.get_json()
    print('Received data:', data)

 # Validate and convert data
    try:
        u_price = float(data.get('u_price'))          # Unitary price of the stock
        u_sale = float(data.get('u_sale'))            # Unitary sale price
        benefit_rate = float(data.get('benefit_rate')) # Expected benefit rate
        expences_F = float(data.get('expences_F'))     # Fixed expenses
        delay_supply = int(data.get('delay_supply'))    # Delay in replenishing stock
        stock_rate = float(data.get('stock_rate'))      # Stock security rate
        order_n = int(data.get('order_n'))              # Expected number of orders
        order_f = int(data.get('order_f'))              # Orders every few days
        due_date = int(data.get('due_date'))            # Simulate for a number of days
        order_q = int(data.get('order_q'))              # Mean order quantity
        order_fluc = float(data.get('order_fluc'))      # Order quantity fluctuation
        
    except (ValueError, TypeError) as e:
        print('Error parsing parameters:', e)
        return jsonify({'error': 'Invalid input data', 'details': str(e)}), 400
    
    # Debugging output
    print('Parameters:')
    print('u_price:', u_price)
    print('u_sale:', u_sale)
    print('benefit_rate:', benefit_rate)
    print('expences_F:', expences_F)
    print('delay_supply:', delay_supply)
    print('stock_rate:', stock_rate)
    print('order_n:', order_n)
    print('order_f:', order_f)
    print('due_date:', due_date)
    print('order_q:', order_q)
    print('order_fluc:', order_fluc)

    # Call to your StockPriceD function (ensure it handles errors gracefully)
    try:
        return StockPriceD(u_price, u_sale, benefit_rate, expences_F, delay_supply, stock_rate, order_n, order_f, due_date, order_q, order_fluc)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)

