"""
Author: Akshat Singh
GitHub: @akshatsingh-dev
Email: akshat@example.com
Date: 2025-07-25
Role: Developer
"""
import yfinance as yf
import pandas as pd
import numpy as np
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockDataCollector:
    """Collects real-time stock data and maintains historical data"""
    
    def __init__(self):
        self.data_cache = {}
        self.is_running = False
        self.collection_thread = None
        
    def fetch_real_time_data(self, symbol: str, period: str = "1d", interval: str = "1m") -> pd.DataFrame:
        """Fetch real-time data for a single stock symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data received for {symbol}")
                return pd.DataFrame()
            
            # Add technical indicators
            data = self._add_technical_indicators(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the data"""
        if len(data) < 20:
            return data
        
        # Simple Moving Averages
        data['SMA_5'] = data['Close'].rolling(window=5).mean()
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        
        # Exponential Moving Averages
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        
        # MACD
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
        data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
        
        # Volume indicators
        data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_Ratio'] = data['Volume'] / data['Volume_SMA']
        
        # Price change indicators
        data['Price_Change'] = data['Close'].pct_change()
        data['Price_Change_5'] = data['Close'].pct_change(periods=5)
        
        return data
    
    def fetch_multiple_symbols(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols"""
        results = {}
        
        for symbol in symbols:
            results[symbol] = self.fetch_real_time_data(symbol)
            time.sleep(Config.API_DELAY)  # Rate limiting
            
        return results
    
    def start_continuous_collection(self, symbols: List[str], callback=None):
        """Start continuous data collection in a separate thread"""
        self.is_running = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            args=(symbols, callback)
        )
        self.collection_thread.start()
        logger.info("Started continuous data collection")
    
    def stop_continuous_collection(self):
        """Stop continuous data collection"""
        self.is_running = False
        if self.collection_thread:
            self.collection_thread.join()
        logger.info("Stopped continuous data collection")
    
    def _collection_loop(self, symbols: List[str], callback=None):
        """Main collection loop"""
        while self.is_running:
            try:
                # Fetch data for all symbols
                new_data = self.fetch_multiple_symbols(symbols)
                
                # Update cache
                for symbol, data in new_data.items():
                    if not data.empty:
                        self.data_cache[symbol] = data
                
                # Call callback with new data
                if callback:
                    callback(new_data)
                
                # Wait before next collection
                time.sleep(Config.UPDATE_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in collection loop: {str(e)}")
                time.sleep(Config.UPDATE_INTERVAL)
    
    def get_cached_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get cached data for a symbol"""
        return self.data_cache.get(symbol)
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest price for a symbol"""
        data = self.get_cached_data(symbol)
        if data is not None and not data.empty:
            return float(data['Close'].iloc[-1])
        return None
    
    def get_price_change(self, symbol: str, periods: int = 1) -> Optional[float]:
        """Get price change over specified periods"""
        data = self.get_cached_data(symbol)
        if data is not None and len(data) > periods:
            current_price = data['Close'].iloc[-1]
            previous_price = data['Close'].iloc[-1-periods]
            return (current_price - previous_price) / previous_price
        return None
    
    def save_data_to_file(self, symbol: str, filename: str = None):
        """Save cached data to CSV file"""
        data = self.get_cached_data(symbol)
        if data is not None:
            if filename is None:
                filename = f"{Config.DATA_DIR}/{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            data.to_csv(filename)
            logger.info(f"Saved data for {symbol} to {filename}")
    
    def load_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Load historical data for model training"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval="1h")
            
            if not data.empty:
                data = self._add_technical_indicators(data)
                
            return data
            
        except Exception as e:
            logger.error(f"Error loading historical data for {symbol}: {str(e)}")
            return pd.DataFrame()
