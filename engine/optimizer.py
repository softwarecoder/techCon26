class OptimizerEngine:
    def __init__(self, debt_info):
        self.debt = debt_info

    def get_debt_recommendations(self):
        """
        Compares Snowball vs Avalanche strategies.
        """
        # Create a list of debt objects
        debts = [
            {
                "name": "Credit Card",
                "balance": self.debt['credit_card_balance'],
                "interest": self.debt['credit_card_interest_rate'] if 'credit_card_interest_rate' in self.debt else 0.18,
                "rate": 0.18 # Defaulting for POC
            },
            {
                "name": "Personal Loan",
                "balance": self.debt['personal_loan_balance'],
                "interest": self.debt['personal_loan_interest_rate'],
                "rate": self.debt['personal_loan_interest_rate']
            }
        ]

        # 1. Debt Snowball Strategy (Smallest Balance First)
        snowball_plan = sorted(debts, key=lambda x: x['balance'])
        snowball_order = " -> ".join([d['name'] for d in snowball_plan])

        # 2. Debt Avalanche Strategy (Highest Interest First)
        avalanche_plan = sorted(debts, key=lambda x: x['rate'], reverse=True)
        avalanche_order = " -> ".join([d['name'] for d in avalanche_plan])

        # 3. Refinance Suggestion
        refinance_needed = "No"
        if any(d['rate'] > 0.12 for d in debts):
            refinance_needed = "YES - Consider consolidating high-interest debt into a lower-rate personal loan."

        return {
            "strategies": {
                "snowball_order": snowball_order,
                "avalanche_order": avalanche_order
            },
            "refinance_recommendation": refinance_needed,
            "total_debt": sum(d['balance'] for d in debts)
        }
