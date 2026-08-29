import datetime

import pandas as pd
import numpy as np

class PredictorEngine:
    def __init__(self, transactions_df):
        self.df = transactions_df

    def predict_cash_flow(self, days_ahead=30):
        """
        Uses linear regression on daily balance to predict future cash flow.
        """
        # 1. Calculate Daily Balance Trend
        self.df['date'] = pd.to_datetime(self.df['date'])
        # Group by date and sum amounts
        daily_net = self.df.groupby(self.df['date'].dt.date)['amount'].sum().reset_index()
        daily_net['date'] = pd.to_datetime(daily_net['date'])
        
        # Calculate cumulative balance
        daily_net['balance'] = daily_net['amount'].cumsum()
        
        # 2. Linear Regression (y = mx + c)
        # Convert dates to ordinal numbers for math
        x = daily_net['date'].map(datetime.datetime.toordinal).values
        y = daily_net['balance'].values
        
        if len(x) < 2:
            return {"error": "Not enough data to predict"}

        # Perform linear fit
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs

        # 3. Predict future balance
        last_date = daily_net['date'].max()
        future_date = last_date + pd.Timedelta(days=days_ahead)
        future_ordinal = future_date.toordinal()
        
        predicted_balance = slope * future_ordinal + intercept

        # 4. Identify Stress Risk
        risk_level = "Low"
        if predicted_balance < 0:
            risk_level = "High (Cash Shortfall Predicted)"
        elif predicted_balance < 500:
            risk_level = "Medium"

        return {
            "current_balance": round(daily_net['balance'].iloc[-1], 2),
            "predicted_balance_30d": round(predicted_balance, 2),
            "risk_level": risk_level,
            "trend_slope": round(slope, 2) # Positive means growing, negative means shrinking
        }
