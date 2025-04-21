import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from enum import Enum


class TrendType(Enum):
    """Enum for trend types"""
    STRONG_UPTREND = "strong_uptrend"
    UPTREND = "uptrend"
    WEAK_UPTREND = "weak_uptrend"
    NEUTRAL = "neutral"
    WEAK_DOWNTREND = "weak_downtrend"
    DOWNTREND = "downtrend"
    STRONG_DOWNTREND = "strong_downtrend"


class TrendDetector:
    """
    A comprehensive trend detection engine that uses multiple methods
    to identify market trends across different timeframes.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with OHLCV price data.
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing 'open', 'high', 'low', 'close', and 'volume' columns
        """
        required_columns = ['open', 'high', 'low', 'close']
        missing = [col for col in required_columns if col not in data.columns]
        
        if missing:
            raise ValueError(f"Data missing required columns: {', '.join(missing)}")
            
        self.data = data.copy()
        # Ensure data is sorted by index (typically date)
        self.data = self.data.sort_index()
    
    def analyze_trends(self) -> pd.DataFrame:
        """
        Apply all trend detection methods and return enhanced DataFrame
        
        Returns:
        --------
        pd.DataFrame: Original data with trend analysis columns added
        """
        df = self.data.copy()
        
        # Calculate Moving Averages for trend reference
        for period in [20, 50, 100, 200]:
            df[f'sma_{period}'] = self._calculate_sma(period)
            df[f'ema_{period}'] = self._calculate_ema(period)
        
        # Add short-term trend detection (based on shorter MAs)
        df['short_term_trend'] = self._detect_trend_by_ma_alignment(
            fast_ma=8, 
            medium_ma=20, 
            slow_ma=50
        )
        
        # Add medium-term trend detection (based on medium MAs)
        df['medium_term_trend'] = self._detect_trend_by_ma_alignment(
            fast_ma=20, 
            medium_ma=50, 
            slow_ma=100
        )
        
        # Add long-term trend detection (based on longer MAs)
        df['long_term_trend'] = self._detect_trend_by_ma_alignment(
            fast_ma=50, 
            medium_ma=100, 
            slow_ma=200
        )
        
        # Add trend detection using higher highs/lows method
        df['hh_ll_trend'] = self._detect_trend_by_higher_highs_lows(lookback=20)
        
        # Add trend detection using linear regression
        df['linreg_trend'] = self._detect_trend_by_linear_regression(lookback=20)
        df['linreg_slope'] = self._calculate_linear_regression_slope(lookback=20)
        
        # Add trend strength index
        df['trend_strength'] = self._calculate_trend_strength()
        
        # Add ADX for trend strength confirmation
        df['adx'] = self._calculate_adx(period=14)
        
        # Determine consolidated trend (combining multiple methods)
        df['consolidated_trend'] = self._calculate_consolidated_trend(df)
        
        # Determine if in trending or ranging market
        df['market_structure'] = self._determine_market_structure(df)
        
        # Add trend duration (how many bars the current trend has lasted)
        df['trend_duration'] = self._calculate_trend_duration(df)
        
        return df
    
    def _calculate_sma(self, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return self.data['close'].rolling(window=period).mean()
    
    def _calculate_ema(self, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return self.data['close'].ewm(span=period, adjust=False).mean()
    
    def _calculate_adx(self, period: int = 14) -> pd.Series:
        """
        Calculate Average Directional Index (ADX) for trend strength
        Simple implementation without requiring external libraries
        """
        df = self.data.copy()
        
        # Calculate +DM and -DM
        df['high_diff'] = df['high'].diff()
        df['low_diff'] = df['low'].diff() * -1
        
        df['+dm'] = np.where(
            (df['high_diff'] > df['low_diff']) & (df['high_diff'] > 0),
            df['high_diff'],
            0
        )
        
        df['-dm'] = np.where(
            (df['low_diff'] > df['high_diff']) & (df['low_diff'] > 0),
            df['low_diff'],
            0
        )
        
        # Calculate True Range
        df['tr0'] = abs(df['high'] - df['low'])
        df['tr1'] = abs(df['high'] - df['close'].shift(1))
        df['tr2'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
        
        # Calculate smoothed values
        df['smoothed_tr'] = df['tr'].rolling(window=period).sum()
        df['smoothed_+dm'] = df['+dm'].rolling(window=period).sum()
        df['smoothed_-dm'] = df['-dm'].rolling(window=period).sum()
        
        # Calculate +DI and -DI
        df['+di'] = 100 * df['smoothed_+dm'] / df['smoothed_tr']
        df['-di'] = 100 * df['smoothed_-dm'] / df['smoothed_tr']
        
        # Calculate DX and ADX
        df['dx'] = 100 * abs(df['+di'] - df['-di']) / (df['+di'] + df['-di'])
        adx = df['dx'].rolling(window=period).mean()
        
        return adx
    
    def _detect_trend_by_ma_alignment(self, fast_ma: int = 8, medium_ma: int = 20, slow_ma: int = 50) -> pd.Series:
        """
        Detect trend using MA alignment (fast MA relative to slow MA)
        
        Parameters:
        -----------
        fast_ma : int
            Period for the fast MA
        medium_ma : int
            Period for the medium MA
        slow_ma : int
            Period for the slow MA
            
        Returns:
        --------
        pd.Series: Series with trend values
        """
        # Calculate required MAs
        ema_fast = self._calculate_ema(fast_ma)
        ema_medium = self._calculate_ema(medium_ma)
        ema_slow = self._calculate_ema(slow_ma)
        price = self.data['close']
        
        # Create trend series
        trend = pd.Series(index=self.data.index, dtype='object')
        
        # Strong uptrend: Price > Fast MA > Medium MA > Slow MA
        strong_uptrend = (
            (price > ema_fast) & 
            (ema_fast > ema_medium) & 
            (ema_medium > ema_slow)
        )
        
        # Uptrend: Price > Medium MA > Slow MA
        uptrend = (
            (price > ema_medium) & 
            (ema_medium > ema_slow) & 
            ~strong_uptrend
        )
        
        # Weak uptrend: Price > Slow MA and (Fast MA or Medium MA < Slow MA)
        weak_uptrend = (
            (price > ema_slow) & 
            (~uptrend) & 
            (~strong_uptrend)
        )
        
        # Strong downtrend: Price < Fast MA < Medium MA < Slow MA
        strong_downtrend = (
            (price < ema_fast) & 
            (ema_fast < ema_medium) & 
            (ema_medium < ema_slow)
        )
        
        # Downtrend: Price < Medium MA < Slow MA
        downtrend = (
            (price < ema_medium) & 
            (ema_medium < ema_slow) & 
            ~strong_downtrend
        )
        
        # Weak downtrend: Price < Slow MA and (Fast MA or Medium MA > Slow MA)
        weak_downtrend = (
            (price < ema_slow) & 
            (~downtrend) & 
            (~strong_downtrend)
        )
        
        # Assign trends
        trend[strong_uptrend] = TrendType.STRONG_UPTREND.value
        trend[uptrend] = TrendType.UPTREND.value
        trend[weak_uptrend] = TrendType.WEAK_UPTREND.value
        trend[strong_downtrend] = TrendType.STRONG_DOWNTREND.value
        trend[downtrend] = TrendType.DOWNTREND.value
        trend[weak_downtrend] = TrendType.WEAK_DOWNTREND.value
        
        # Default to neutral where no other condition is met
        trend[trend.isnull()] = TrendType.NEUTRAL.value
        
        return trend
    
    def _detect_trend_by_higher_highs_lows(self, lookback: int = 20) -> pd.Series:
        """
        Detect trend using higher highs and higher lows (for uptrend)
        or lower highs and lower lows (for downtrend)
        
        Parameters:
        -----------
        lookback : int
            Number of periods to look back
            
        Returns:
        --------
        pd.Series: Series with trend values
        """
        df = self.data.copy()
        
        # Create a series to store trend values
        trend = pd.Series(index=df.index, dtype='object')
        trend.iloc[:lookback] = TrendType.NEUTRAL.value
        
        for i in range(lookback, len(df)):
            window = df.iloc[i-lookback:i]
            current_close = df['close'].iloc[i]
            
            # Find significant swing highs and lows in the window
            # (simplified - in practice would need more sophisticated detection)
            highs = window['high'].rolling(5, center=True).max()
            lows = window['low'].rolling(5, center=True).min()
            
            # Count higher highs and higher lows
            higher_highs = highs.diff().dropna() > 0
            higher_lows = lows.diff().dropna() > 0
            
            # Get the trend state
            hh_count = higher_highs.sum()
            hl_count = higher_lows.sum()
            
            lh_count = (~higher_highs).sum()
            ll_count = (~higher_lows).sum()
            
            # Determine trend based on combinations of HH, HL, LH, LL
            if hh_count > lh_count and hl_count > ll_count:
                if hh_count > lookback * 0.7 and hl_count > lookback * 0.7:
                    trend.iloc[i] = TrendType.STRONG_UPTREND.value
                else:
                    trend.iloc[i] = TrendType.UPTREND.value
            elif lh_count > hh_count and ll_count > hl_count:
                if lh_count > lookback * 0.7 and ll_count > lookback * 0.7:
                    trend.iloc[i] = TrendType.STRONG_DOWNTREND.value
                else:
                    trend.iloc[i] = TrendType.DOWNTREND.value
            else:
                # Mixed signals, could be transitioning or ranging
                trend.iloc[i] = TrendType.NEUTRAL.value
        
        return trend
    
    def _detect_trend_by_linear_regression(self, lookback: int = 20) -> pd.Series:
        """
        Detect trend using linear regression slope
        
        Parameters:
        -----------
        lookback : int
            Number of periods to look back
            
        Returns:
        --------
        pd.Series: Series with trend values
        """
        df = self.data.copy()
        
        # Create a series to store trend values
        trend = pd.Series(index=df.index, dtype='object')
        trend.iloc[:lookback] = TrendType.NEUTRAL.value
        
        for i in range(lookback, len(df)):
            # Get close prices for the lookback period
            prices = df['close'].iloc[i-lookback:i].values
            
            # Create array of x values (0 to lookback-1)
            x = np.arange(lookback)
            
            # Calculate slope using linear regression
            slope, _ = np.polyfit(x, prices, 1)
            
            # Calculate average price to normalize slope
            avg_price = np.mean(prices)
            normalized_slope = slope / avg_price * 100  # as percentage
            
            # Classify trend based on slope strength
            if normalized_slope > 1.0:
                trend.iloc[i] = TrendType.STRONG_UPTREND.value
            elif normalized_slope > 0.5:
                trend.iloc[i] = TrendType.UPTREND.value
            elif normalized_slope > 0.1:
                trend.iloc[i] = TrendType.WEAK_UPTREND.value
            elif normalized_slope < -1.0:
                trend.iloc[i] = TrendType.STRONG_DOWNTREND.value
            elif normalized_slope < -0.5:
                trend.iloc[i] = TrendType.DOWNTREND.value
            elif normalized_slope < -0.1:
                trend.iloc[i] = TrendType.WEAK_DOWNTREND.value
            else:
                trend.iloc[i] = TrendType.NEUTRAL.value
        
        return trend
    
    def _calculate_linear_regression_slope(self, lookback: int = 20) -> pd.Series:
        """
        Calculate linear regression slope for each point in the series
        
        Parameters:
        -----------
        lookback : int
            Number of periods to look back
            
        Returns:
        --------
        pd.Series: Series with normalized slope values
        """
        df = self.data.copy()
        
        # Create a series to store slope values
        slope_series = pd.Series(index=df.index)
        slope_series.iloc[:lookback-1] = np.nan
        
        for i in range(lookback, len(df)):
            # Get close prices for the lookback period
            prices = df['close'].iloc[i-lookback:i].values
            
            # Create array of x values (0 to lookback-1)
            x = np.arange(lookback)
            
            # Calculate slope using linear regression
            slope, _ = np.polyfit(x, prices, 1)
            
            # Calculate average price to normalize slope
            avg_price = np.mean(prices)
            normalized_slope = slope / avg_price * 100  # as percentage
            
            slope_series.iloc[i-1] = normalized_slope
        
        return slope_series
    
    def _calculate_trend_strength(self) -> pd.Series:
        """
        Calculate trend strength on a scale from 0-100
        Combines multiple trend indicators
        
        Returns:
        --------
        pd.Series: Series with trend strength values (0-100)
        """
        df = self.data.copy()
        
        # Calculate ADX for trend strength component (0-40 points max)
        adx = self._calculate_adx(period=14)
        adx_score = adx.clip(0, 60) * (40/60)  # Scale to 0-40
        
        # Moving average alignment component (0-30 points max)
        ema_9 = self._calculate_ema(9)
        ema_20 = self._calculate_ema(20)
        ema_50 = self._calculate_ema(50)
        
        ma_align_score = pd.Series(0, index=df.index)
        
        # Strong alignment: all MAs aligned in order
        strong_alignment = (
            ((df['close'] > ema_9) & (ema_9 > ema_20) & (ema_20 > ema_50)) |  # bullish
            ((df['close'] < ema_9) & (ema_9 < ema_20) & (ema_20 < ema_50))    # bearish
        )
        
        # Medium alignment: price and slower MAs aligned
        medium_alignment = (
            ((df['close'] > ema_20) & (ema_20 > ema_50) & ~strong_alignment) |  # bullish
            ((df['close'] < ema_20) & (ema_20 < ema_50) & ~strong_alignment)    # bearish
        )
        
        ma_align_score[strong_alignment] = 30
        ma_align_score[medium_alignment] = 15
        
        # Volatility component: stable trend has lower volatility (0-30 points max)
        volatility_score = pd.Series(30, index=df.index)
        
        # Calculate historical volatility
        log_returns = np.log(df['close'] / df['close'].shift(1))
        volatility = log_returns.rolling(window=20).std() * np.sqrt(252) * 100  # annualized and in percent
        
        # Higher volatility = lower score (inverse relationship)
        volatility_score = 30 - volatility.clip(0, 30)  # 0-30 range
        
        # Combine scores
        trend_strength = adx_score + ma_align_score + volatility_score
        
        # Ensure range is 0-100
        return trend_strength.clip(0, 100)
    
    def _calculate_consolidated_trend(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate consolidated trend by combining multiple trend detection methods
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with trend columns
            
        Returns:
        --------
        pd.Series: Series with consolidated trend values
        """
        # Create a series to store consolidated trend
        consolidated_trend = pd.Series(index=df.index, dtype='object')
        
        # Define trend columns and their respective weights
        trend_columns = {
            'short_term_trend': 0.4,    # 40% weight for short-term
            'medium_term_trend': 0.3,   # 30% weight for medium-term
            'long_term_trend': 0.1,     # 10% weight for long-term
            'hh_ll_trend': 0.1,         # 10% weight for HH/LL method
            'linreg_trend': 0.1         # 10% weight for linear regression
        }
        
        # Create a numerical mapping for trend values
        trend_mapping = {
            TrendType.STRONG_UPTREND.value: 3,
            TrendType.UPTREND.value: 2,
            TrendType.WEAK_UPTREND.value: 1,
            TrendType.NEUTRAL.value: 0,
            TrendType.WEAK_DOWNTREND.value: -1,
            TrendType.DOWNTREND.value: -2,
            TrendType.STRONG_DOWNTREND.value: -3
        }
        
        # Create numerical columns for weighted calculation
        numerical_trends = pd.DataFrame(index=df.index)
        
        for col, weight in trend_columns.items():
            if col in df.columns:
                numerical_trends[col] = df[col].map(trend_mapping) * weight
        
        # Calculate weighted sum
        weighted_sum = numerical_trends.sum(axis=1)
        
        # Map weighted sum back to trend types
        consolidated_trend[(weighted_sum >= 2)] = TrendType.STRONG_UPTREND.value
        consolidated_trend[(weighted_sum >= 1) & (weighted_sum < 2)] = TrendType.UPTREND.value
        consolidated_trend[(weighted_sum > 0) & (weighted_sum < 1)] = TrendType.WEAK_UPTREND.value
        consolidated_trend[(weighted_sum > -1) & (weighted_sum <= 0)] = TrendType.NEUTRAL.value
        consolidated_trend[(weighted_sum <= -2)] = TrendType.STRONG_DOWNTREND.value
        consolidated_trend[(weighted_sum <= -1) & (weighted_sum > -2)] = TrendType.DOWNTREND.value
        consolidated_trend[(weighted_sum < 0) & (weighted_sum > -1)] = TrendType.WEAK_DOWNTREND.value
        
        return consolidated_trend
    
    def _determine_market_structure(self, df: pd.DataFrame) -> pd.Series:
        """
        Determine if market is trending or ranging
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with trend strength and ADX
            
        Returns:
        --------
        pd.Series: Series with market structure (trending or ranging)
        """
        market_structure = pd.Series(index=df.index, dtype='object')
        
        # Use trend strength and ADX to determine market structure
        trending_market = (
            (df['trend_strength'] > 55) |  # Strong trend strength
            (df['adx'] > 25)               # ADX above trending threshold
        )
        
        market_structure[trending_market] = 'trending'
        market_structure[~trending_market] = 'ranging'
        
        return market_structure
    
    def _calculate_trend_duration(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate how many bars the current trend has lasted
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with consolidated trend
            
        Returns:
        --------
        pd.Series: Series with trend duration in bars
        """
        if 'consolidated_trend' not in df.columns:
            return pd.Series(np.nan, index=df.index)
        
        # Initialize a series to store trend duration
        duration = pd.Series(1, index=df.index)
        
        # For each row after the first, check if trend is the same as previous
        for i in range(1, len(df)):
            if df['consolidated_trend'].iloc[i] == df['consolidated_trend'].iloc[i-1]:
                duration.iloc[i] = duration.iloc[i-1] + 1
        
        return duration
    
    def get_trend_summary(self, lookback: int = 5) -> Dict:
        """
        Get a summary of trend analysis for recent data
        
        Parameters:
        -----------
        lookback : int
            Number of bars to look back
            
        Returns:
        --------
        Dict: Summary of trend analysis
        """
        # First analyze all trends
        df = self.analyze_trends()
        
        # Get recent data
        recent_data = df.iloc[-lookback:].copy()
        
        # Get the latest trend values
        latest_trends = {
            'short_term': recent_data['short_term_trend'].iloc[-1],
            'medium_term': recent_data['medium_term_trend'].iloc[-1],
            'long_term': recent_data['long_term_trend'].iloc[-1],
            'consolidated': recent_data['consolidated_trend'].iloc[-1]
        }
        
        # Get latest metrics
        latest_metrics = {
            'trend_strength': recent_data['trend_strength'].iloc[-1],
            'adx': recent_data['adx'].iloc[-1],
            'market_structure': recent_data['market_structure'].iloc[-1],
            'trend_duration': recent_data['trend_duration'].iloc[-1],
            'linear_regression_slope': recent_data['linreg_slope'].iloc[-1]
        }
        
        # Determine if trends are aligned
        trends_aligned = (
            (latest_trends['short_term'] == latest_trends['medium_term']) and
            (latest_trends['medium_term'] == latest_trends['long_term'])
        )
        
        # Determine momentum (accelerating or decelerating)
        trend_changes = recent_data['consolidated_trend'].astype(str).shift(1) != recent_data['consolidated_trend']
        recent_change = trend_changes.sum() > 0
        
        # Determine if trend is strengthening or weakening
        strength_change = recent_data['trend_strength'].iloc[-1] - recent_data['trend_strength'].iloc[0]
        
        trend_momentum = "stable"
        if strength_change > 5:
            trend_momentum = "strengthening"
        elif strength_change < -5:
            trend_momentum = "weakening"
        
        return {
            'current_trends': latest_trends,
            'metrics': latest_metrics,
            'trends_aligned': trends_aligned,
            'trend_momentum': trend_momentum,
            'recent_trend_change': recent_change
        }


# Example usage
def analyze_trends(df: pd.DataFrame) -> pd.DataFrame:
    return TrendDetector(df).analyze_trends()

def get_trend_summary(df: pd.DataFrame, lookback: int = 5) -> Dict:
    return TrendDetector(df).get_trend_summary(lookback)


if __name__ == "__main__":
    import yfinance as yf

    print("📥 Downloading sample data for NIFTY...")
    data = yf.download("^NSEI", period="6mo", interval="1d", auto_adjust=False)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.columns = [col.lower() for col in data.columns]

    # Analyze trends
    print("🔍 Analyzing market trends...")
    result = analyze_trends(data)

    # Get trend summary
    summary = get_trend_summary(data)
    
    print("\n✅ Trend Analysis Complete!")
    print(f"Current Consolidated Trend: {summary['current_trends']['consolidated']}")
    print(f"Short-term Trend: {summary['current_trends']['short_term']}")
    print(f"Medium-term Trend: {summary['current_trends']['medium_term']}")
    print(f"Long-term Trend: {summary['current_trends']['long_term']}")
    print(f"Trend Strength: {summary['metrics']['trend_strength']:.2f}/100")
    print(f"ADX: {summary['metrics']['adx']:.2f}")
    print(f"Market Structure: {summary['metrics']['market_structure']}")
    print(f"Trend Duration: {summary['metrics']['trend_duration']} bars")
    print(f"Trend Momentum: {summary['trend_momentum']}")
    print(f"Trends Aligned: {'Yes' if summary['trends_aligned'] else 'No'}")
    
    # Save the results
    result.to_csv("trend_analysis.csv")
    print("\n📁 Full analysis saved to trend_analysis.csv")