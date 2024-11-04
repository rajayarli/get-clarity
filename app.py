import os
from flask import Flask, render_template, request, jsonify
from LoanCalculator import LoanCalculator
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
app = Flask(__name__)

# Function to fetch real-time conversion rates
def get_conversion_rate(from_currency, to_currency, api_key):
    url = f'https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}'
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and data['result'] == 'success':
        return data['conversion_rate']
    else:
        raise Exception(f"Error fetching conversion rate: {data.get('error-type', 'Unknown error')}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # Retrieve input values
    currency = request.form['currency']
    salary_currency = request.form['salary_currency']
    loan_amount = float(request.form['loan_amount'])
    interest_rate = float(request.form['interest_rate'])
    tenure = int(request.form['tenure'])
    tenure_type = request.form['tenure_type']
    start_date = request.form['start_date']
    salary = float(request.form['salary'])
    savings_percentage = int(request.form['savings']) / 100
    desired_timeline_months = int(request.form['timeline'])  # User's desired timeline in months

    # Convert tenure to months if necessary
    tenure_months = tenure * 12 if tenure_type == 'years' else tenure

    # Loan calculator for EMI and schedule using the original loan tenure
    calculator = LoanCalculator(loan_amount, interest_rate, tenure_months / 12)
    emi = calculator.calculate_emi()
    schedule = calculator.generate_amortization_schedule()
    
    # Calculate completion date based on desired timeline
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    completion_date_obj = start_date_obj + timedelta(days=(desired_timeline_months * 30))
    completion_date = completion_date_obj.strftime('%d/%m/%y')  # Format as dd/mm/yy

    # Adjusted EMI for desired repayment timeline (e.g., 6 months)
    adjusted_calculator = LoanCalculator(loan_amount, interest_rate, desired_timeline_months / 12)
    min_payment = adjusted_calculator.calculate_emi()

    # Fetch real-time conversion rate
    api_key = os.getenv('EXCHANGE_API_KEY')  # Use environment variable for security
    loan_to_salary_rate = get_conversion_rate(currency, salary_currency, api_key)

    # Convert EMI and minimum payment to salary currency
    emi_in_salary_currency = emi * loan_to_salary_rate
    min_payment_in_salary_currency = min_payment * loan_to_salary_rate

    # Convert salary to loan currency
    salary_in_loan_currency = salary * get_conversion_rate(salary_currency, currency, api_key)
    monthly_savings = salary_in_loan_currency * savings_percentage
    is_affordable = monthly_savings >= min_payment

    # Send results back
    return jsonify({
        'emi': f"{emi:.2f} {currency} / {emi_in_salary_currency:.2f} {salary_currency}",
        'currency': currency,
        'salary_currency': salary_currency,
        'completion_date': completion_date,
        'min_payment': f"{min_payment:.2f} {currency} / {min_payment_in_salary_currency:.2f} {salary_currency}",
        'is_affordable': is_affordable,
        'schedule': schedule
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Heroku provides $PORT
    app.run(host='0.0.0.0', port=port, debug=True)
