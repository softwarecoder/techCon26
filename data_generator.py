import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

class LATAMDataGenerator:
    def __init__(self, locale='pt_BR'):
        """
        Initialize with LATAM locales. 
        'pt_BR' for Brazil, 'es_MX' for Mexico.
        """
        self.fake = Faker(locale)
        
        # LATAM Specific Merchants to make the POC look real
        self.merchants = {
            'Food': ['iFood', 'Rappi', 'Mercado Libre Food', 'Local Supermarket', 'OXXO', 'Carrefour'],
            'Transport': ['Uber', '99App', 'Local Bus', 'Gas Station'],
            'Utilities': ['Netflix', 'Spotify', 'Local Electric Co', 'Water Dept', 'Internet Provider'],
            'Shopping': ['Mercado Libre', 'Amazon', 'Shopee', 'Local Mall'],
            'Health': ['Pharmacy', 'Local Clinic', 'Hospital'],
            'Entertainment': ['Cinema', 'Steam', 'Local Bar']
        }
        
        self.categories = list(self.merchants.keys())

    def generate_user_profile(self):
        """Generates a basic user identity."""
        return {
            "user_id": self.fake.uuid4(),
            "name": self.fake.name(),
            "email": self.fake.email(),
            "location": self.fake.city(),
            "currency": "BRL" if self.fake.locale == 'pt_BR' else "MXN",
            "monthly_income_avg": round(random.uniform(3000, 8000), 2)
        }

    def generate_transactions(self, days_back=90):
        """Generates a time-series of transactions."""
        transactions = []
        start_date = datetime.now() - timedelta(days=days_back)
        current_date = start_date

        # 1. Generate Monthly Salary (Fixed Income)
        # We assume salary hits on the 1st of every month
        for i in range(days_back // 30 + 2):
            salary_date = datetime(current_date.year, current_date.month, 1)
            if salary_date >= start_date:
                transactions.append({
                    'date': salary_date,
                    'amount': round(random.uniform(4500, 5500), 2), # Salary varies slightly
                    'category': 'Income',
                    'merchant': 'Employer Salary',
                    'type': 'Income'
                })

        # 2. Generate Regular Expenses
        while current_date <= datetime.now():
            # Skip if it's already a salary day to avoid overlap
            if current_date.day == 1:
                current_date += timedelta(days=1)
                continue

            # Randomly decide if a transaction happens today (60% chance)
            if random.random() > 0.4:
                category = random.choice(self.categories)
                merchant = random.choice(self.merchants[category])
                
                # Logic to make some expenses larger (Rent/Utilities) and some small (Food)
                if category in ['Utilities', 'Rent']:
                    amount = round(random.uniform(500, 1500), 2)
                elif category == 'Food':
                    amount = round(random.uniform(20, 150), 2)
                else:
                    amount = round(random.uniform(50, 400), 2)

                transactions.append({
                    'date': current_date,
                    'amount': -amount, # Expenses are negative
                    'category': category,
                    'merchant': merchant,
                    'type': 'Expense'
                })
            
            current_date += timedelta(days=1)

        df = pd.DataFrame(transactions)
        return df.sort_values(by='date').reset_index(drop=True)

    def generate_debt_data(self):
        """Generates existing debt profiles for the user (Crucial for Module 3)."""
        return {
            'credit_card_balance': round(random.uniform(1000, 5000), 2),
            'credit_card_limit': 10000.0,
            'personal_loan_balance': round(random.uniform(5000, 20000), 2),
            'personal_loan_interest_rate': 0.15, # 15% APR
            'installment_plan_monthly': round(random.uniform(300, 800), 2)
        }

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    print("🚀 Starting LATAM Data Generation...")
    
    # Initialize generator (using Mexico locale for this example)
    generator = LATAMDataGenerator(locale='es_MX')
    
    # 1. Generate Profile
    user = generator.generate_user_profile()
    print(f"👤 User Generated: {user['name']} from {user['location']}")

    # 2. Generate Transactions
    transactions_df = generator.generate_transactions(days_back=90)
    print(f"💰 Transactions Generated: {len(transactions_df)} rows")

    # 3. Generate Debt
    debt = generator.generate_debt_data()
    print(f"💳 Debt Info Generated: Card Balance ${debt['credit_card_balance']}")

    # 4. Save to CSV for use in other modules
    transactions_df.to_csv("user_transactions.csv", index=False)
    
    # Save user profile and debt as JSON for easy loading
    import json
    with open("user_profile.json", "w") as f:
        json.dump({"profile": user, "debt": debt}, f)

    print("\n✅ SUCCESS!")
    print("Files created: 'user_transactions.csv' and 'user_profile.json'")
    print("You can now use these files to test your Analytics and AI modules.")
