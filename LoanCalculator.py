class LoanCalculator:
    def __init__(self, loan_amount, interest_rate, tenure_years):
        self.loan_amount = loan_amount
        self.interest_rate = interest_rate / 100 / 12  # Monthly interest rate
        self.tenure_months = int(tenure_years * 12)  # Total months

    def calculate_emi(self):
        # EMI calculation formula
        emi = (self.loan_amount * self.interest_rate * (1 + self.interest_rate) ** self.tenure_months) / \
              ((1 + self.interest_rate) ** self.tenure_months - 1)
        return round(emi, 2)

    def generate_amortization_schedule(self):
        # Generate monthly breakdown of EMI, interest, principal, and balance
        emi = self.calculate_emi()
        balance = self.loan_amount
        schedule = []
        for month in range(1, self.tenure_months + 1):
            interest_payment = balance * self.interest_rate
            principal_payment = emi - interest_payment
            balance -= principal_payment
            schedule.append({
                'Month': month,
                'EMI': round(emi, 2),
                'Interest Payment': round(interest_payment, 2),
                'Principal Payment': round(principal_payment, 2),
                'Balance': round(balance, 2)
            })
        return schedule
