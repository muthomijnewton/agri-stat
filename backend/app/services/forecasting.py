"""
Forecasting service for demand prediction using Prophet and ARIMA
"""

from typing import List, Dict, Tuple, Optional
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.models.models import Transaction, Forecast, Product
from app.core.config import FORECAST_DAYS, FORECAST_MODEL

try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False


class ForecastingService:
    """Service for demand forecasting"""
    
    @staticmethod
    def get_transaction_history(db: Session, product_id: int, days: int = 90) -> pd.DataFrame:
        """
        Retrieve transaction history for a product
        
        Args:
            db: Database session
            product_id: Product ID
            days: Number of days of history to retrieve
            
        Returns:
            DataFrame with ds (date) and y (quantity) columns
        """
        start_date = date.today() - timedelta(days=days)
        
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.product_id == product_id,
                Transaction.transaction_date >= start_date
            )
        ).order_by(Transaction.transaction_date).all()
        
        if not transactions:
            return pd.DataFrame(columns=['ds', 'y'])
        
        # Aggregate by date
        df = pd.DataFrame([
            {'ds': t.transaction_date, 'y': t.quantity}
            for t in transactions
        ])
        
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Group by date and sum quantities
        df = df.groupby('ds')['y'].sum().reset_index()
        df = df.sort_values('ds')
        
        return df
    
    @staticmethod
    def forecast_prophet(df: pd.DataFrame, periods: int = FORECAST_DAYS) -> Tuple[List[Dict], float]:
        """
        Forecast using Facebook Prophet
        
        Args:
            df: DataFrame with 'ds' and 'y' columns
            periods: Number of periods to forecast
            
        Returns:
            Tuple of (forecasts list, accuracy score)
        """
        if not PROPHET_AVAILABLE or df.empty:
            return [], 0.0
        
        try:
            # Initialize and fit Prophet model
            model = Prophet(yearly_seasonality=True, daily_seasonality=False)
            model.fit(df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            
            # Get only future forecasts
            future_forecast = forecast[forecast['ds'] > df['ds'].max()][
                ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
            ].copy()
            
            # Calculate MAPE (Mean Absolute Percentage Error) on historical data
            historical_forecast = forecast[forecast['ds'] <= df['ds'].max()].copy()
            historical_forecast = historical_forecast.merge(df, on='ds')
            
            mape = np.mean(np.abs((historical_forecast['y'] - historical_forecast['yhat']) / 
                                 (historical_forecast['y'] + 1))) * 100
            
            # Convert to list of dicts
            forecasts = [
                {
                    'date': row['ds'].date(),
                    'predicted_demand': max(0, int(round(row['yhat']))),
                    'lower': max(0, int(round(row['yhat_lower']))),
                    'upper': max(0, int(round(row['yhat_upper'])))
                }
                for _, row in future_forecast.iterrows()
            ]
            
            return forecasts, min(mape, 100.0)  # Cap at 100%
            
        except Exception as e:
            print(f"Error in Prophet forecast: {e}")
            return [], 0.0
    
    @staticmethod
    def forecast_arima(df: pd.DataFrame, periods: int = FORECAST_DAYS) -> Tuple[List[Dict], float]:
        """
        Forecast using ARIMA
        
        Args:
            df: DataFrame with 'ds' and 'y' columns
            periods: Number of periods to forecast
            
        Returns:
            Tuple of (forecasts list, accuracy score)
        """
        if not ARIMA_AVAILABLE or df.empty or len(df) < 10:
            return [], 0.0
        
        try:
            # Fit ARIMA model (order=(1,1,1) is a common starting point)
            model = ARIMA(df['y'], order=(1, 1, 1))
            result = model.fit()
            
            # Get forecast
            forecast_result = result.get_forecast(steps=periods)
            forecast_df = forecast_result.summary_frame()
            
            # Calculate MAPE
            mape = np.mean(np.abs((df['y'].iloc[-10:].values - result.fittedvalues.iloc[-10:].values) / 
                                  (df['y'].iloc[-10:].values + 1))) * 100
            
            # Convert to list of dicts
            forecasts = [
                {
                    'date': (df['ds'].max() + timedelta(days=i+1)).date(),
                    'predicted_demand': max(0, int(round(forecast_df['mean'].iloc[i]))),
                    'lower': max(0, int(round(forecast_df['mean_ci_lower'].iloc[i]))),
                    'upper': max(0, int(round(forecast_df['mean_ci_upper'].iloc[i])))
                }
                for i in range(len(forecast_df))
            ]
            
            return forecasts, min(mape, 100.0)
            
        except Exception as e:
            print(f"Error in ARIMA forecast: {e}")
            return [], 0.0
    
    @staticmethod
    def generate_forecast(db: Session, product_id: int, forecast_type: str = FORECAST_MODEL) -> List[Dict]:
        """
        Generate demand forecast for a product
        
        Args:
            db: Database session
            product_id: Product ID
            forecast_type: 'prophet', 'arima', or 'auto'
            
        Returns:
            List of forecast dictionaries
        """
        # Get historical data
        df = ForecastingService.get_transaction_history(db, product_id)
        
        if df.empty:
            # Return simple linear forecast if no history
            return []
        
        # Select forecasting method
        if forecast_type == 'prophet':
            forecasts, accuracy = ForecastingService.forecast_prophet(df)
        elif forecast_type == 'arima':
            forecasts, accuracy = ForecastingService.forecast_arima(df)
        else:  # auto
            # Try Prophet first, fallback to ARIMA
            forecasts, accuracy = ForecastingService.forecast_prophet(df)
            if not forecasts:
                forecasts, accuracy = ForecastingService.forecast_arima(df)
        
        # Store forecasts in database
        for forecast_data in forecasts:
            forecast = Forecast(
                product_id=product_id,
                forecast_date=forecast_data['date'],
                predicted_demand=forecast_data['predicted_demand'],
                confidence_lower=forecast_data.get('lower'),
                confidence_upper=forecast_data.get('upper'),
                model_type=forecast_type,
                accuracy_score=accuracy
            )
            db.add(forecast)
        
        db.commit()
        return forecasts
    
    @staticmethod
    def calculate_inventory_recommendation(db: Session, product_id: int) -> Dict:
        """
        Calculate recommended inventory quantity based on forecast
        
        Args:
            db: Database session
            product_id: Product ID
            
        Returns:
            Dictionary with recommendation data
        """
        # Get recent forecasts
        forecasts = db.query(Forecast).filter(
            Forecast.product_id == product_id
        ).order_by(Forecast.forecast_date).limit(FORECAST_DAYS).all()
        
        if not forecasts:
            return {'recommended_quantity': 0, 'reason': 'No forecasts available'}
        
        # Calculate average predicted demand
        total_demand = sum(f.predicted_demand for f in forecasts)
        avg_daily_demand = total_demand / len(forecasts)
        
        # Apply safety stock formula: Recommended = Avg Demand * Lead time + Safety Stock
        # Assuming 3-day lead time and 1.5 safety factor
        lead_time = 3
        safety_factor = 1.5
        
        recommended = int(avg_daily_demand * lead_time * safety_factor)
        
        return {
            'recommended_quantity': recommended,
            'average_daily_demand': round(avg_daily_demand, 2),
            'reason': f'Based on {len(forecasts)} days of forecasted demand'
        }


# Import needed for type hints
from sqlalchemy import and_
