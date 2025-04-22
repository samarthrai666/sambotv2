import pandas as pd
import numpy as np
from typing import Optional, Union, Dict, List, Tuple
import talib
from scipy import stats


class TradingIndicators:
    """
    A comprehensive class for calculating professional trading indicators
    with configurable parameters and advanced analysis techniques.
    """
    
    def __init__(self, data):
        """
        Initialize with OHLCV price data.
        
        Parameters:
        -----------
        data : pd.DataFrame or dict
            DataFrame containing 'open', 'high', 'low', 'close', and 'volume' columns
            or dictionary with 'candles' key
        """
        # Convert data to DataFrame if it's a dictionary
        if isinstance(data, dict) and 'candles' in data:
            candles = data['candles']
            data = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])

        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required_columns if col not in data.columns]
        
        if missing:
            raise ValueError(f"Data missing required columns: {', '.join(missing)}")
            
        self.data = data.copy()
        # Ensure data is sorted by index (typically date)
        self.data = self.data.sort_index()

    def calculate_all(self) -> pd.DataFrame:
        """Calculate all available indicators and return enhanced DataFrame"""
        df = self.data.copy()
        
        # Price action indicators
        df = self.add_support_resistance(df)
        
        # Trend indicators
        df['sma_20'] = self.sma(period=20)
        df['sma_50'] = self.sma(period=50)
        df['sma_200'] = self.sma(period=200)
        df['ema_9'] = self.ema(period=9)
        df['ema_21'] = self.ema(period=21)
        df['ema_55'] = self.ema(period=55)
        df['tema_9'] = self.tema(period=9)
        
        # Volatility indicators
        df['atr_14'] = self.atr(period=14)
        df['bbands_upper'], df['bbands_middle'], df['bbands_lower'] = self.bollinger_bands(period=20, std_dev=2)
        df['bb_width'] = (df['bbands_upper'] - df['bbands_lower']) / df['bbands_middle']
        df['keltner_upper'], df['keltner_middle'], df['keltner_lower'] = self.keltner_channels(ema_period=20, atr_period=10, atr_multiplier=2)
        df['bb_kc_squeeze'] = self.bollinger_keltner_squeeze(bb_length=20, kc_length=20, kc_multiplier=2)
        
        # Momentum indicators
        df['rsi_14'] = self.rsi(period=14)
        df['rsi_2'] = self.rsi(period=2)
        df['stoch_k'], df['stoch_d'] = self.stochastic(k_period=14, d_period=3, slowing=3)
        df['macd'], df['macd_signal'], df['macd_hist'] = self.macd(fast_period=12, slow_period=26, signal_period=9)
        df['cci'] = self.cci(period=14)
        df['williams_r'] = self.williams_r(period=14)
        df['adx'] = self.adx(period=14)
        df['di_plus'] = self.di_plus(period=14)
        df['di_minus'] = self.di_minus(period=14)
        df['mfi'] = self.money_flow_index(period=14)
        
        # Volume indicators
        df['obv'] = self.on_balance_volume()
        df['vwap'] = self.vwap()
        df['cmf'] = self.chaikin_money_flow(period=20)
        df['adl'] = self.accumulation_distribution_line()
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['rel_volume'] = df['volume'] / df['volume_sma_20']
        
        # Advanced indicators
        df['heikin_ashi_open'], df['heikin_ashi_high'], df['heikin_ashi_low'], df['heikin_ashi_close'] = self.heikin_ashi()
        df['ichimoku_conversion'], df['ichimoku_base'], df['ichimoku_span_a'], df['ichimoku_span_b'] = self.ichimoku_cloud()
        df['fisher_transform'] = self.fisher_transform(period=10)
        
        # Signal generators
        df['buy_signal_ema_cross'] = ((df['ema_9'] > df['ema_21']) & (df['ema_9'].shift(1) <= df['ema_21'].shift(1))).astype(int)
        df['sell_signal_ema_cross'] = ((df['ema_9'] < df['ema_21']) & (df['ema_9'].shift(1) >= df['ema_21'].shift(1))).astype(int)
        df['buy_signal_macd'] = ((df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int)
        df['sell_signal_macd'] = ((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))).astype(int)
        df['overbought'] = (df['rsi_14'] > 70).astype(int)
        df['oversold'] = (df['rsi_14'] < 30).astype(int)
        
        # Generate market regime and trend strength
        df['market_regime'] = self.market_regime()
        df['trend_strength'] = self.trend_strength()
        
        return df
        
    # ========== TREND INDICATORS ==========
    
    def sma(self, period: int = 20) -> pd.Series:
        """Simple Moving Average"""
        return self.data['close'].rolling(window=period).mean()
    
    def ema(self, period: int = 20) -> pd.Series:
        """Exponential Moving Average"""
        return talib.EMA(self.data['close'], timeperiod=period)
    
    def tema(self, period: int = 20) -> pd.Series:
        """Triple Exponential Moving Average"""
        return talib.TEMA(self.data['close'], timeperiod=period)
        
    def dema(self, period: int = 20) -> pd.Series:
        """Double Exponential Moving Average"""
        return talib.DEMA(self.data['close'], timeperiod=period)
    
    # ========== VOLATILITY INDICATORS ==========
    
    def atr(self, period: int = 14) -> pd.Series:
        """Average True Range"""
        return talib.ATR(self.data['high'], self.data['low'], self.data['close'], timeperiod=period)
    
    def bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands
        
        Returns:
        --------
        upper, middle, lower : Tuple[pd.Series, pd.Series, pd.Series]
        """
        middle = self.data['close'].rolling(window=period).mean()
        std = self.data['close'].rolling(window=period).std()
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        return upper, middle, lower
    
    def keltner_channels(self, ema_period: int = 20, atr_period: int = 10, atr_multiplier: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Keltner Channels
        
        Returns:
        --------
        upper, middle, lower : Tuple[pd.Series, pd.Series, pd.Series]
        """
        middle = talib.EMA(self.data['close'], timeperiod=ema_period)
        atr_val = talib.ATR(self.data['high'], self.data['low'], self.data['close'], timeperiod=atr_period)
        upper = middle + atr_multiplier * atr_val
        lower = middle - atr_multiplier * atr_val
        return upper, middle, lower
    
    def bollinger_keltner_squeeze(self, bb_length: int = 20, kc_length: int = 20, kc_multiplier: float = 2.0) -> pd.Series:
        """
        Bollinger Bands and Keltner Channel Squeeze (John Carter)
        Returns 1 when Bollinger Bands are inside Keltner Channels (squeeze)
        """
        bb_upper, _, bb_lower = self.bollinger_bands(period=bb_length)
        kc_upper, _, kc_lower = self.keltner_channels(ema_period=kc_length, atr_multiplier=kc_multiplier)
        squeeze = (bb_upper < kc_upper) & (bb_lower > kc_lower)
        return squeeze.astype(int)
    
    # ========== MOMENTUM INDICATORS ==========
    
    def rsi(self, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        return talib.RSI(self.data['close'], timeperiod=period)
    
    def stochastic(self, k_period: int = 14, d_period: int = 3, slowing: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator
        
        Returns:
        --------
        k, d : Tuple[pd.Series, pd.Series]
            %K and %D lines
        """
        k, d = talib.STOCH(self.data['high'], self.data['low'], self.data['close'], 
                           fastk_period=k_period, slowk_period=slowing, 
                           slowk_matype=0, slowd_period=d_period, slowd_matype=0)
        return k, d
    
    
    def macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Moving Average Convergence Divergence
        
        Returns:
        --------
        macd, signal, histogram : Tuple[pd.Series, pd.Series, pd.Series]
        """
        macd, signal, hist = talib.MACD(self.data['close'], fastperiod=fast_period, 
                                        slowperiod=slow_period, signalperiod=signal_period)
        return macd, signal, hist
    
    def cci(self, period: int = 14) -> pd.Series:
        """Commodity Channel Index"""
        return talib.CCI(self.data['high'], self.data['low'], self.data['close'], timeperiod=period)
    
    def williams_r(self, period: int = 14) -> pd.Series:
        """Williams %R"""
        return talib.WILLR(self.data['high'], self.data['low'], self.data['close'], timeperiod=period)
    
    def adx(self, period: int = 14) -> pd.Series:
        """Average Directional Index"""
        return talib.ADX(self.data['high'], self.data['low'], self.data['close'], timeperiod=period)
    
    def di_plus(self, period: int = 14) -> pd.Series:
        """Positive Directional Indicator"""
        return talib.PLUS_DI(self.data['high'], self.data['low'], self.data['close'], timeperiod=period)
    
    def di_minus(self, period: int = 14) -> pd.Series:
        """Negative Directional Indicator"""
        return talib.MINUS_DI(self.data['high'], self.data['low'], self.data['close'], timeperiod=period)
    
    def money_flow_index(self, period: int = 14) -> pd.Series:
        """Money Flow Index"""
        return talib.MFI(self.data['high'], self.data['low'], self.data['close'], self.data['volume'], timeperiod=period)
    
    # ========== VOLUME INDICATORS ==========
    
    def on_balance_volume(self) -> pd.Series:
        """On Balance Volume"""
        return talib.OBV(self.data['close'], self.data['volume'])
    
    def vwap(self) -> pd.Series:
        """
        Volume Weighted Average Price
        """
        df = self.data.copy()
        
        # Calculate typical price
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        # Calculate price * volume
        df['pv'] = typical_price * df['volume']
        
        # For grouping, we'll create a simple date grouping
        # If we can't use the index, create artificial groups
        try:
            if isinstance(df.index, pd.DatetimeIndex):
                df['date_group'] = df.index.date
            elif 'timestamp' in df.columns:
                # Try to convert timestamp column to datetime
                df['date_group'] = pd.to_datetime(df['timestamp']).dt.date
            else:
                # Group every 75 rows as a "day" (arbitrary number for intraday)
                df['date_group'] = [i // 75 for i in range(len(df))]
        except:
            # Fallback to a single group if all else fails
            df['date_group'] = 0
        
        # Calculate cumulative values for each group
        df['cum_pv'] = df.groupby('date_group')['pv'].cumsum()
        df['cum_vol'] = df.groupby('date_group')['volume'].cumsum()
        
        # Calculate VWAP
        vwap_series = df['cum_pv'] / df['cum_vol'].replace(0, 1)  # Avoid division by zero
        
        return vwap_series
    
    def chaikin_money_flow(self, period: int = 20) -> pd.Series:
        """Chaikin Money Flow"""
        df = self.data.copy()
        
        # Calculate Money Flow Multiplier
        df['mfm'] = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        df['mfm'] = df['mfm'].replace([np.inf, -np.inf], 0)  # Handle division by zero
        
        # Calculate Money Flow Volume
        df['mfv'] = df['mfm'] * df['volume']
        
        # Calculate Chaikin Money Flow
        cmf = df['mfv'].rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
        return cmf
    
    def accumulation_distribution_line(self) -> pd.Series:
        """Accumulation/Distribution Line"""
        return talib.AD(self.data['high'], self.data['low'], self.data['close'], self.data['volume'])
    
    # ========== PRICE ACTION INDICATORS ==========
    
    def add_support_resistance(self, df: pd.DataFrame, window: int = 10, threshold: float = 0.02) -> pd.DataFrame:
        """
        Identify potential support and resistance zones using local extrema
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with OHLC data
        window : int
            Lookback window to identify extrema
        threshold : float
            Percentage proximity to consider a price level as testing support/resistance
            
        Returns:
        --------
        pd.DataFrame: DataFrame with support/resistance columns added
        """
        # Find local maxima and minima
        df['local_min'] = df['low'].rolling(window=window, center=True).apply(
            lambda x: 1 if (len(x) > window//2 and x.iloc[window//2] == min(x) and x.iloc[window//2] != x.iloc[window//2-1]) else 0,
            raw=False
        )
        df['local_max'] = df['high'].rolling(window=window, center=True).apply(
            lambda x: 1 if (len(x) > window//2 and x.iloc[window//2] == max(x) and x.iloc[window//2] != x.iloc[window//2-1]) else 0,
            raw=False
        )
        
        # Extract levels
        support_levels = df.loc[df['local_min'] == 1, 'low'].tolist()
        resistance_levels = df.loc[df['local_max'] == 1, 'high'].tolist()
        
        # Check if price is testing support or resistance
        df['at_support'] = 0
        df['at_resistance'] = 0
        
        for i, row in df.iterrows():
            # Check support levels
            for level in support_levels:
                if abs(row['low'] - level) / level < threshold:
                    df.at[i, 'at_support'] = 1
                    break
                    
            # Check resistance levels
            for level in resistance_levels:
                if abs(row['high'] - level) / level < threshold:
                    df.at[i, 'at_resistance'] = 1
                    break
        
        return df
    
    # ========== ADVANCED INDICATORS ==========
    
    def heikin_ashi(self) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        Heikin-Ashi candles
        
        Returns:
        --------
        ha_open, ha_high, ha_low, ha_close : Tuple[pd.Series, pd.Series, pd.Series, pd.Series]
        """
        df = self.data.copy()
        
        # Calculate Heikin-Ashi Close
        ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        
        # Calculate Heikin-Ashi Open
        ha_open = pd.Series(index=df.index)
        ha_open.iloc[0] = df['open'].iloc[0]
        for i in range(1, len(df)):
            ha_open.iloc[i] = (ha_open.iloc[i-1] + ha_close.iloc[i-1]) / 2
        
        # Calculate Heikin-Ashi High and Low
        ha_high = pd.Series(index=df.index)
        ha_low = pd.Series(index=df.index)
        for i in range(len(df)):
            ha_high.iloc[i] = max(df['high'].iloc[i], ha_open.iloc[i], ha_close.iloc[i])
            ha_low.iloc[i] = min(df['low'].iloc[i], ha_open.iloc[i], ha_close.iloc[i])
        
        return ha_open, ha_high, ha_low, ha_close
    
    def ichimoku_cloud(self, conversion_period: int = 9, base_period: int = 26, 
                      span_b_period: int = 52, displacement: int = 26) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        Ichimoku Cloud indicator
        
        Returns:
        --------
        conversion, base, span_a, span_b : Tuple[pd.Series, pd.Series, pd.Series, pd.Series]
        """
        df = self.data.copy()
        
        # Tenkan-sen (Conversion Line): (period high + period low)/2
        period_high = df['high'].rolling(window=conversion_period).max()
        period_low = df['low'].rolling(window=conversion_period).min()
        conversion = (period_high + period_low) / 2
        
        # Kijun-sen (Base Line): (period high + period low)/2
        period_high = df['high'].rolling(window=base_period).max()
        period_low = df['low'].rolling(window=base_period).min()
        base = (period_high + period_low) / 2
        
        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2
        span_a = ((conversion + base) / 2).shift(displacement)
        
        # Senkou Span B (Leading Span B): (period high + period low)/2
        period_high = df['high'].rolling(window=span_b_period).max()
        period_low = df['low'].rolling(window=span_b_period).min()
        span_b = ((period_high + period_low) / 2).shift(displacement)
        
        return conversion, base, span_a, span_b
        
    
    def fisher_transform(self, period: int = 10) -> pd.Series:
        """
        Fisher Transform indicator
        Transforms prices into a Gaussian normal distribution
        """
        df = self.data.copy()
        
        # Calculate position within the range
        median_price = (df['high'] + df['low']) / 2
        rolling_min = median_price.rolling(window=period).min()
        rolling_max = median_price.rolling(window=period).max()
        
        # Scale values to -1 to 1 range
        value = pd.Series(index=df.index, dtype=float)
        value_idx = ((rolling_max - rolling_min) != 0)
        value[value_idx] = 2 * ((median_price - rolling_min) / (rolling_max - rolling_min) - 0.5)
        value = value.clip(-0.999, 0.999)  # Clip to avoid log(infinity) issues
        
        # Apply Fisher Transform
        fisher = 0.5 * np.log((1 + value) / (1 - value))
        
        return fisher
    
    # ========== MARKET CLASSIFICATION ==========
    
    
    def market_regime(self) -> pd.Series:
        """
        Classify market regime
        
        Returns:
        --------
        pd.Series with values: 'strong_uptrend', 'uptrend', 'neutral', 'downtrend', 'strong_downtrend'
        """
        # Calculate necessary indicators if not already in data
        sma_20 = self.sma(period=20)
        sma_50 = self.sma(period=50)
        sma_200 = self.sma(period=200)
        adx = self.adx(period=14)
        
        # Define conditions
        strong_uptrend = (
            (self.data['close'] > sma_20) & 
            (sma_20 > sma_50) & 
            (sma_50 > sma_200) & 
            (adx > 25)
        )
        
        uptrend = (
            (self.data['close'] > sma_50) & 
            (sma_50 > sma_200)
        )
        
        strong_downtrend = (
            (self.data['close'] < sma_20) & 
            (sma_20 < sma_50) & 
            (sma_50 < sma_200) & 
            (adx > 25)
        )
        
        downtrend = (
            (self.data['close'] < sma_50) & 
            (sma_50 < sma_200)
        )
        
        # Assign regimes
        regime = pd.Series(index=self.data.index, dtype=str)
        regime[strong_uptrend] = 'strong_uptrend'
        regime[~strong_uptrend & uptrend] = 'uptrend'
        regime[strong_downtrend] = 'strong_downtrend'
        regime[~strong_downtrend & downtrend] = 'downtrend'
        regime[regime.isnull()] = 'neutral'
        
        return regime
    
    def trend_strength(self) -> pd.Series:
        """
        Calculate trend strength score (0-100)
        Combines ADX, Moving Averages relationship and RSI
        
        Returns:
        --------
        pd.Series with values 0-100 (0: no trend, 100: extremely strong trend)
        """
        # Calculate indicators if needed
        adx = self.adx(period=14)
        rsi = self.rsi(period=14)
        ema_9 = self.ema(period=9)
        ema_21 = self.ema(period=21)
        ema_50 = self.ema(period=50)
        
        # ADX contribution (0-40 points)
        adx_score = adx * (40/100)
        
        # Moving average alignment (0-30 points)
        ma_align_score = pd.Series(0, index=self.data.index)
        
        # Uptrend alignment
        uptrend_align = (
            (ema_9 > ema_21) & 
            (ema_21 > ema_50) & 
            (self.data['close'] > ema_9)
        )
        
        # Downtrend alignment
        downtrend_align = (
            (ema_9 < ema_21) & 
            (ema_21 < ema_50) & 
            (self.data['close'] < ema_9)
        )
        
        ma_align_score[uptrend_align | downtrend_align] = 30
        
        # RSI extremes contribution (0-30 points)
        rsi_score = pd.Series(0, index=self.data.index)
        rsi_score[(rsi > 70) | (rsi < 30)] = 30 * (
            (rsi > 70).astype(int) + (rsi < 30).astype(int)
        )
        
        # Combine scores
        total_score = adx_score + ma_align_score + rsi_score
        
        # Ensure range is 0-100
        return total_score.clip(0, 100)


# Example usage
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    return TradingIndicators(df).calculate_all()


if __name__ == "__main__":
    import yfinance as yf

    print("📥 Downloading sample data for NIFTY...")
    data = yf.download("^NSEI", period="3mo", interval="1d", auto_adjust=False)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.columns = [col.lower() for col in data.columns]

    result = calculate_indicators(data)

    print("✅ Indicator Calculation Done:")
    print(result.tail())

    result.to_csv("output_indicators.csv")
    print("📁 Saved to output_indicators.csv")