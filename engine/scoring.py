import pandas as pd

class ScoringEngine:
    def __init__(self, transactions_df, debt_info, user_profile):
        self.df = transactions_df
        self.debt = debt_info
        self.profile = user_profile

    def calculate_fhs(self):
        """
        Calculates a Financial Health Score (0-100).
        Weights: 
        - Savings Ratio: 35%
        - Debt Utilization: 35%
        - Spending Discipline: 30%
        """
        # 1. Savings Ratio Calculation
        income = self.df[self.df['type'] == 'Income']['amount'].sum()
        expenses = abs(self.df[self.df['type'] == 'Expense']['amount'].sum())
        savings = income - expenses
        savings_ratio = (savings / income) if income > 0 else 0
        # Normalize savings ratio (target 20% savings = 100 score)
        savings_score = min(100, (savings_ratio / 0.20) * 100)

        # 2. Debt Utilization Calculation
        total_debt = self.debt['credit_card_balance'] + self.debt['personal_loan_balance']
        # High debt relative to income lowers the score
        debt_to_income = total_debt / self.profile['monthly_income_avg']
        # target debt_to_income < 0.3 (30%) for 100 score
        debt_score = max(0, 100 - (debt_to_income / 0.3 * 100))

        # 3. Spending Discipline (Volatility)
        # We measure how much daily spending fluctuates. High volatility = lower score.
        daily_spending = self.df[self.df['type'] == 'Expense'].groupby(self.df['date'].dt.date)['amount'].sum().abs()
        if not daily_spending.empty:
            volatility = daily_spending.std() / daily_spending.mean()
            # Normalize: Low volatility (~0) = 100 score, High volatility (>1.0) = 0 score
            discipline_score = max(0, 100 - (volatility * 100))
        else:
            discipline_score = 50

        # Final Weighted Score
        final_score = (
            (savings_score * 0.35) + 
            (debt_score * 0.35) + 
            (discipline_score * 0.30)
        )

        return {
            "final_score": round(final_score, 2),
            "breakdown": {
                "savings_score": round(savings_score, 2),
                "debt_score": round(debt_score, 2),
                "discipline_score": round(discipline_score, 2)
            },
            "metrics": {
                "savings_ratio": round(savings_ratio, 2),
                "debt_to_income": round(debt_to_income, 2)
            }
        }
