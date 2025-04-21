import pandas as pd
import numpy as np
import talib
from typing import Dict, List, Tuple, Optional, Union
from scipy import stats
from scipy.signal import find_peaks


class PatternEngine:
    """
    A comprehensive pattern recognition engine for trading that detects
    both candlestick patterns and chart patterns.
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
    
    def detect_all_patterns(self) -> pd.DataFrame:
        """
        Detect all patterns (candlestick and chart patterns) and return enhanced DataFrame
        
        Returns:
        --------
        pd.DataFrame: Original data with pattern columns added
        """
        df = self.data.copy()
        
        # Add candlestick patterns
        df = self.detect_candlestick_patterns(df)
        
        # Add chart patterns
        df = self.detect_chart_patterns(df)
        
        # Calculate pattern scores and summaries
        df = self.calculate_pattern_scores(df)
        
        return df
    
    def detect_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect candlestick patterns using TA-Lib
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with OHLC data
            
        Returns:
        --------
        pd.DataFrame: DataFrame with candlestick pattern columns added
        """
        # Dictionary to map pattern names with their respective detection functions
        candlestick_patterns = {
            # Bullish reversal patterns
            'cdl_hammer': talib.CDLHAMMER,
            'cdl_inv_hammer': talib.CDLINVERTEDHAMMER,
            'cdl_engulfing_bull': lambda o, h, l, c: (talib.CDLENGULFING(o, h, l, c) > 0).astype(int),
            'cdl_morning_star': talib.CDLMORNINGSTAR,
            'cdl_morning_doji_star': talib.CDLMORNINGDOJISTAR,
            'cdl_piercing': talib.CDLPIERCING,
            'cdl_harami_bull': lambda o, h, l, c: (talib.CDLHARAMI(o, h, l, c) > 0).astype(int),
            'cdl_dragonfly_doji': talib.CDLDRAGONFLYDOJI,
            
            # Bearish reversal patterns
            'cdl_shooting_star': talib.CDLSHOOTINGSTAR,
            'cdl_hanging_man': talib.CDLHANGINGMAN,
            'cdl_engulfing_bear': lambda o, h, l, c: (talib.CDLENGULFING(o, h, l, c) < 0).astype(int),
            'cdl_evening_star': talib.CDLEVENINGSTAR,
            'cdl_evening_doji_star': talib.CDLEVENINGDOJISTAR,
            'cdl_dark_cloud_cover': talib.CDLDARKCLOUDCOVER,
            'cdl_harami_bear': lambda o, h, l, c: (talib.CDLHARAMI(o, h, l, c) < 0).astype(int),
            'cdl_gravestone_doji': talib.CDLGRAVESTONEDOJI,
            
            # Continuation patterns
            'cdl_doji': talib.CDLDOJI,
            'cdl_spinning_top': talib.CDLSPINNINGTOP,
            'cdl_marubozu': talib.CDLMARUBOZU,
            'cdl_3_white_soldiers': talib.CDL3WHITESOLDIERS,
            'cdl_3_black_crows': talib.CDL3BLACKCROWS,
            'cdl_3_inside_up': talib.CDL3INSIDE,
            'cdl_3_outside': talib.CDL3OUTSIDE
        }
        
        # Detect each pattern
        for pattern_name, pattern_func in candlestick_patterns.items():
            df[pattern_name] = pattern_func(df['open'], df['high'], df['low'], df['close'])
            # Convert non-zero values to 1 for consistency
            df[pattern_name] = df[pattern_name].apply(lambda x: 1 if x != 0 else 0)
        
        # Create lists of bullish and bearish patterns for easy reference
        bullish_patterns = [
            'cdl_hammer', 'cdl_inv_hammer', 'cdl_engulfing_bull', 'cdl_morning_star',
            'cdl_morning_doji_star', 'cdl_piercing', 'cdl_harami_bull', 'cdl_dragonfly_doji',
            'cdl_3_white_soldiers', 'cdl_3_inside_up'
        ]
        
        bearish_patterns = [
            'cdl_shooting_star', 'cdl_hanging_man', 'cdl_engulfing_bear', 'cdl_evening_star',
            'cdl_evening_doji_star', 'cdl_dark_cloud_cover', 'cdl_harami_bear', 'cdl_gravestone_doji',
            'cdl_3_black_crows'
        ]
        
        # Add indicator columns for any bullish or bearish pattern
        df['any_bullish_candlestick'] = df[bullish_patterns].any(axis=1).astype(int)
        df['any_bearish_candlestick'] = df[bearish_patterns].any(axis=1).astype(int)
        
        # Count the number of bullish and bearish patterns
        df['bullish_candlestick_count'] = df[bullish_patterns].sum(axis=1)
        df['bearish_candlestick_count'] = df[bearish_patterns].sum(axis=1)
        
        return df
    
    def detect_chart_patterns(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        Detect chart patterns like double tops/bottoms, head and shoulders, etc.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with OHLC data
        window : int
            Lookback window to detect patterns
            
        Returns:
        --------
        pd.DataFrame: DataFrame with chart pattern columns added
        """
        # Initialize all chart pattern columns
        chart_patterns = [
            'double_top', 'double_bottom', 'head_shoulders', 'inv_head_shoulders',
            'triangle_ascending', 'triangle_descending', 'triangle_symmetrical',
            'channel_up', 'channel_down', 'wedge_rising', 'wedge_falling',
            'flag_bull', 'flag_bear', 'pennant_bull', 'pennant_bear'
        ]
        
        for pattern in chart_patterns:
            df[pattern] = 0
        
        # Detect each type of pattern
        self._detect_double_top_bottom(df, window)
        self._detect_head_and_shoulders(df, window)
        self._detect_triangles(df, window)
        self._detect_channels_and_wedges(df, window)
        self._detect_flags_and_pennants(df, window)
        
        # Create lists of bullish and bearish chart patterns
        bullish_chart_patterns = [
            'double_bottom', 'inv_head_shoulders', 'triangle_ascending',
            'channel_up', 'wedge_falling', 'flag_bull', 'pennant_bull'
        ]
        
        bearish_chart_patterns = [
            'double_top', 'head_shoulders', 'triangle_descending',
            'channel_down', 'wedge_rising', 'flag_bear', 'pennant_bear'
        ]
        
        # Add indicator columns for any bullish or bearish chart pattern
        df['any_bullish_chart'] = df[bullish_chart_patterns].any(axis=1).astype(int)
        df['any_bearish_chart'] = df[bearish_chart_patterns].any(axis=1).astype(int)
        
        # Count the number of bullish and bearish chart patterns
        df['bullish_chart_count'] = df[bullish_chart_patterns].sum(axis=1)
        df['bearish_chart_count'] = df[bearish_chart_patterns].sum(axis=1)
        
        return df
    
    def calculate_pattern_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate pattern scores and create summary columns
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with pattern columns
            
        Returns:
        --------
        pd.DataFrame: DataFrame with pattern scores added
        """
        # Calculate candlestick pattern score (bullish - bearish)
        if 'bullish_candlestick_count' in df.columns and 'bearish_candlestick_count' in df.columns:
            df['candlestick_pattern_score'] = df['bullish_candlestick_count'] - df['bearish_candlestick_count']
        
        # Calculate chart pattern score (bullish - bearish)
        if 'bullish_chart_count' in df.columns and 'bearish_chart_count' in df.columns:
            df['chart_pattern_score'] = df['bullish_chart_count'] - df['bearish_chart_count']
        
        # Calculate overall pattern score (combined with weights)
        # Chart patterns are usually stronger signals, so we weight them more
        if 'candlestick_pattern_score' in df.columns and 'chart_pattern_score' in df.columns:
            df['overall_pattern_score'] = df['candlestick_pattern_score'] + (df['chart_pattern_score'] * 2)
        
        # Add pattern bias column (bullish/bearish/neutral)
        df['pattern_bias'] = 'neutral'
        df.loc[df['overall_pattern_score'] > 2, 'pattern_bias'] = 'strongly_bullish'
        df.loc[(df['overall_pattern_score'] > 0) & (df['overall_pattern_score'] <= 2), 'pattern_bias'] = 'bullish'
        df.loc[df['overall_pattern_score'] < -2, 'pattern_bias'] = 'strongly_bearish'
        df.loc[(df['overall_pattern_score'] < 0) & (df['overall_pattern_score'] >= -2), 'pattern_bias'] = 'bearish'
        
        return df
    
    def _detect_double_top_bottom(self, df: pd.DataFrame, window: int = 20) -> None:
        """
        Detect double top and double bottom patterns
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with OHLC data
        window : int
            Lookback window to detect patterns
        """
        for i in range(window, len(df)):
            # Select window of data to analyze
            window_data = df.iloc[i-window:i+1].copy()
            
            # Find peaks and troughs using scipy's find_peaks
            # For peaks (tops)
            peaks, _ = find_peaks(window_data['high'].values, prominence=0.5)
            
            # For troughs (bottoms)
            troughs, _ = find_peaks(-window_data['low'].values, prominence=0.5)
            
            # Check for double top (two peaks of similar height)
            if len(peaks) >= 2:
                # Sort peaks by height (descending)
                peak_heights = window_data['high'].iloc[peaks].values
                sorted_peaks = peaks[np.argsort(-peak_heights)]
                
                # Take the two highest peaks
                if len(sorted_peaks) >= 2:
                    peak1, peak2 = sorted(sorted_peaks[:2])
                    
                    # Check if peaks are of similar height (within 1%)
                    peak1_height = window_data['high'].iloc[peak1]
                    peak2_height = window_data['high'].iloc[peak2]
                    
                    if (abs(peak1_height - peak2_height) / peak1_height < 0.01 and 
                        peak2 - peak1 >= 3):  # Ensure peaks are separated in time
                        
                        # Check if there's a trough between the peaks
                        troughs_between = [t for t in troughs if peak1 < t < peak2]
                        if troughs_between:
                            # Confirm if the most recent bar is showing rejection from the second peak
                            if window_data['close'].iloc[-1] < window_data['close'].iloc[peak2]:
                                df.loc[df.index[i], 'double_top'] = 1
            
            # Check for double bottom (two troughs of similar depth)
            if len(troughs) >= 2:
                # Sort troughs by depth (ascending)
                trough_depths = window_data['low'].iloc[troughs].values
                sorted_troughs = troughs[np.argsort(trough_depths)]
                
                # Take the two lowest troughs
                if len(sorted_troughs) >= 2:
                    trough1, trough2 = sorted(sorted_troughs[:2])
                    
                    # Check if troughs are of similar depth (within 1%)
                    trough1_depth = window_data['low'].iloc[trough1]
                    trough2_depth = window_data['low'].iloc[trough2]
                    
                    if (abs(trough1_depth - trough2_depth) / trough1_depth < 0.01 and 
                        trough2 - trough1 >= 3):  # Ensure troughs are separated in time
                        
                        # Check if there's a peak between the troughs
                        peaks_between = [p for p in peaks if trough1 < p < trough2]
                        if peaks_between:
                            # Confirm if the most recent bar is showing bounce from the second trough
                            if window_data['close'].iloc[-1] > window_data['close'].iloc[trough2]:
                                df.loc[df.index[i], 'double_bottom'] = 1
    
    def _detect_head_and_shoulders(self, df: pd.DataFrame, window: int = 20) -> None:
        """
        Detect head and shoulders and inverse head and shoulders patterns
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with OHLC data
        window : int
            Lookback window to detect patterns
        """
        for i in range(window, len(df)):
            # Select window of data to analyze
            window_data = df.iloc[i-window:i+1].copy()
            
            # Find peaks and troughs
            peaks, _ = find_peaks(window_data['high'].values, prominence=0.5)
            troughs, _ = find_peaks(-window_data['low'].values, prominence=0.5)
            
            # Head and Shoulders (top formation, bearish)
            if len(peaks) >= 3 and len(troughs) >= 2:
                # Check each sequence of 3 peaks
                for j in range(len(peaks) - 2):
                    # Get three consecutive peaks
                    p1, p2, p3 = peaks[j], peaks[j+1], peaks[j+2]
                    
                    # Head should be higher than shoulders
                    head_value = window_data['high'].iloc[p2]
                    left_shoulder = window_data['high'].iloc[p1]
                    right_shoulder = window_data['high'].iloc[p3]
                    
                    # Check pattern criteria:
                    # 1. Middle peak (head) is higher than both shoulders
                    # 2. Shoulders are roughly at the same level (within 5%)
                    if (head_value > left_shoulder * 1.02 and 
                        head_value > right_shoulder * 1.02 and 
                        abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):
                        
                        # Check for neckline (troughs between the peaks)
                        troughs_between = [t for t in troughs if p1 < t < p3]
                        if len(troughs_between) >= 2:
                            # Check if the most recent bar is breaking below the neckline
                            neckline = min(window_data['low'].iloc[troughs_between])
                            if window_data['close'].iloc[-1] < neckline:
                                df.loc[df.index[i], 'head_shoulders'] = 1
            
            # Inverse Head and Shoulders (bottom formation, bullish)
            if len(troughs) >= 3 and len(peaks) >= 2:
                # Check each sequence of 3 troughs
                for j in range(len(troughs) - 2):
                    # Get three consecutive troughs
                    t1, t2, t3 = troughs[j], troughs[j+1], troughs[j+2]
                    
                    # Head should be lower than shoulders
                    head_value = window_data['low'].iloc[t2]
                    left_shoulder = window_data['low'].iloc[t1]
                    right_shoulder = window_data['low'].iloc[t3]
                    
                    # Check pattern criteria:
                    # 1. Middle trough (head) is lower than both shoulders
                    # 2. Shoulders are roughly at the same level (within 5%)
                    if (head_value < left_shoulder * 0.98 and 
                        head_value < right_shoulder * 0.98 and
                        abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):
                        
                        # Check for neckline (peaks between the troughs)
                        peaks_between = [p for p in peaks if t1 < p < t3]
                        if len(peaks_between) >= 2:
                            # Check if the most recent bar is breaking above the neckline
                            neckline = max(window_data['high'].iloc[peaks_between])
                            if window_data['close'].iloc[-1] > neckline:
                                df.loc[df.index[i], 'inv_head_shoulders'] = 1
    
    def _detect_triangles(self, df: pd.DataFrame, window: int = 20) -> None:
        """
        Detect triangle patterns: ascending, descending, and symmetrical
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with OHLC data
        window : int
            Lookback window to detect patterns
        """
        for i in range(window, len(df)):
            # Select window of data to analyze
            window_data = df.iloc[i-window:i+1].copy()
            
            # Find peaks and troughs
            peaks, _ = find_peaks(window_data['high'].values, prominence=0.5)
            troughs, _ = find_peaks(-window_data['low'].values, prominence=0.5)
            
            # Need at least 2 peaks and 2 troughs to form triangle
            if len(peaks) >= 2 and len(troughs) >= 2:
                # Get x and y coordinates for peaks and troughs
                peak_x = peaks
                peak_y = window_data['high'].iloc[peaks].values
                
                trough_x = troughs
                trough_y = window_data['low'].iloc[troughs].values
                
                # Calculate slope and intercept for upper line (peaks)
                if len(peak_x) >= 2:
                    upper_slope, upper_intercept = np.polyfit(peak_x, peak_y, 1)
                else:
                    continue
                
                # Calculate slope and intercept for lower line (troughs)
                if len(trough_x) >= 2:
                    lower_slope, lower_intercept = np.polyfit(trough_x, trough_y, 1)
                else:
                    continue
                
                # Check for triangle patterns
                
                # Ascending Triangle: flat upper line (resistance), rising lower line (support)
                if abs(upper_slope) < 0.001 and lower_slope > 0.001:
                    if self._verify_triangle_touches(window_data, peak_x, peak_y, trough_x, trough_y,
                                                   upper_slope, upper_intercept, lower_slope, lower_intercept):
                        df.loc[df.index[i], 'triangle_ascending'] = 1
                
                # Descending Triangle: flat lower line (support), falling upper line (resistance)
                elif abs(lower_slope) < 0.001 and upper_slope < -0.001:
                    if self._verify_triangle_touches(window_data, peak_x, peak_y, trough_x, trough_y,
                                                   upper_slope, upper_intercept, lower_slope, lower_intercept):
                        df.loc[df.index[i], 'triangle_descending'] = 1
                
                # Symmetrical Triangle: upper line slopes down, lower line slopes up
                elif upper_slope < -0.001 and lower_slope > 0.001:
                    if self._verify_triangle_touches(window_data, peak_x, peak_y, trough_x, trough_y,
                                                   upper_slope, upper_intercept, lower_slope, lower_intercept):
                        df.loc[df.index[i], 'triangle_symmetrical'] = 1
    
    def _detect_channels_and_wedges(self, df: pd.DataFrame, window: int = 20) -> None:
        """
        Detect price channels and wedges
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with OHLC data
        window : int
            Lookback window to detect patterns
        """
        for i in range(window, len(df)):
            # Select window of data to analyze
            window_data = df.iloc[i-window:i+1].copy()
            
            # Find peaks and troughs
            peaks, _ = find_peaks(window_data['high'].values, prominence=0.5)
            troughs, _ = find_peaks(-window_data['low'].values, prominence=0.5)
            
            # Need at least 2 peaks and 2 troughs to form channels/wedges
            if len(peaks) >= 2 and len(troughs) >= 2:
                # Get x and y coordinates for peaks and troughs
                peak_x = peaks
                peak_y = window_data['high'].iloc[peaks].values
                
                trough_x = troughs
                trough_y = window_data['low'].iloc[troughs].values
                
                # Calculate slope and intercept for upper line (peaks)
                upper_slope, upper_intercept = np.polyfit(peak_x, peak_y, 1)
                
                # Calculate slope and intercept for lower line (troughs)
                lower_slope, lower_intercept = np.polyfit(trough_x, trough_y, 1)
                
                # Check for channels
                
                # Ascending Channel: parallel lines moving up
                if upper_slope > 0.001 and lower_slope > 0.001:
                    # Check if slopes are similar (parallel lines)
                    if abs(upper_slope - lower_slope) / abs(upper_slope) < 0.2:
                        if self._verify_channel_touches(window_data, peak_x, peak_y, trough_x, trough_y,
                                                      upper_slope, upper_intercept, lower_slope, lower_intercept):
                            df.loc[df.index[i], 'channel_up'] = 1
                
                # Descending Channel: parallel lines moving down
                elif upper_slope < -0.001 and lower_slope < -0.001:
                    # Check if slopes are similar (parallel lines)
                    if abs(upper_slope - lower_slope) / abs(upper_slope) < 0.2:
                        if self._verify_channel_touches(window_data, peak_x, peak_y, trough_x, trough_y,
                                                      upper_slope, upper_intercept, lower_slope, lower_intercept):
                            df.loc[df.index[i], 'channel_down'] = 1
                
                # Check for wedges
                
                # Rising Wedge (bearish): both lines moving up, upper line has shallower slope
                if upper_slope > 0.001 and lower_slope > 0.001 and upper_slope < lower_slope:
                    if self._verify_channel_touches(window_data, peak_x, peak_y, trough_x, trough_y,
                                                  upper_slope, upper_intercept, lower_slope, lower_intercept):
                        df.loc[df.index[i], 'wedge_rising'] = 1
                
                # Falling Wedge (bullish): both lines moving down, lower line has shallower slope
                elif upper_slope < -0.001 and lower_slope < -0.001 and upper_slope < lower_slope:
                    if self._verify_channel_touches(window_data, peak_x, peak_y, trough_x, trough_y,
                                                  upper_slope, upper_intercept, lower_slope, lower_intercept):
                        df.loc[df.index[i], 'wedge_falling'] = 1
    
    def _detect_flags_and_pennants(self, df: pd.DataFrame, window: int = 20, pole_window: int = 10) -> None:
        """
        Detect flags and pennants after strong price moves
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with OHLC data
        window : int
            Lookback window for the flag/pennant pattern
        pole_window : int
            Lookback window for the flagpole (strong move)
        """
        for i in range(window + pole_window, len(df)):
            # Get data for flagpole and consolidation (flag/pennant)
            pole_data = df.iloc[i-window-pole_window:i-window+1].copy()
            flag_data = df.iloc[i-window:i+1].copy()
            
            # Calculate price change for the flagpole
            pole_change = (pole_data['close'].iloc[-1] - pole_data['close'].iloc[0]) / pole_data['close'].iloc[0]
            
            # Check for bullish flag/pennant: strong up move followed by consolidation
            if pole_change > 0.05:  # 5% or more move up
                # Calculate price change and trend during the consolidation
                flag_slope, _ = np.polyfit(range(len(flag_data)), flag_data['close'].values, 1)
                
                # Bullish Flag: slight downward drift (counter-trend consolidation)
                if -0.005 < flag_slope < 0:
                    # Check if the consolidation has narrowing range (typical of flags)
                    first_half_range = flag_data['high'].iloc[:len(flag_data)//2].max() - flag_data['low'].iloc[:len(flag_data)//2].min()
                    second_half_range = flag_data['high'].iloc[len(flag_data)//2:].max() - flag_data['low'].iloc[len(flag_data)//2:].min()
                    
                    if second_half_range <= first_half_range:
                        df.loc[df.index[i], 'flag_bull'] = 1
                
                # Bullish Pennant: converging trendlines (symmetric triangle after uptrend)
                high_slope, _ = np.polyfit(range(len(flag_data)), flag_data['high'].values, 1)
                low_slope, _ = np.polyfit(range(len(flag_data)), flag_data['low'].values, 1)
                
                if high_slope < -0.001 and low_slope > 0.001:
                    # Check if the ranges are narrowing (converging trendlines)
                    first_half_range = flag_data['high'].iloc[:len(flag_data)//2].max() - flag_data['low'].iloc[:len(flag_data)//2].min()
                    second_half_range = flag_data['high'].iloc[len(flag_data)//2:].max() - flag_data['low'].iloc[len(flag_data)//2:].min()
                    
                    if second_half_range < first_half_range * 0.8:
                        df.loc[df.index[i], 'pennant_bull'] = 1
            
            # Check for bearish flag/pennant: strong down move followed by consolidation
            elif pole_change < -0.05:  # 5% or more move down
                # Calculate price change and trend during the consolidation
                flag_slope, _ = np.polyfit(range(len(flag_data)), flag_data['close'].values, 1)
                
                # Bearish Flag: slight upward drift (counter-trend consolidation)
                if 0 < flag_slope < 0.005:
                    # Check if the consolidation has narrowing range (typical of flags)
                    first_half_range = flag_data['high'].iloc[:len(flag_data)//2].max() - flag_data['low'].iloc[:len(flag_data)//2].min()
                    second_half_range = flag_data['high'].iloc[len(flag_data)//2:].max() - flag_data['low'].iloc[len(flag_data)//2:].min()
                    
                    if second_half_range <= first_half_range:
                        df.loc[df.index[i], 'flag_bear'] = 1
                
                # Bearish Pennant: converging trendlines (symmetric triangle after downtrend)
                high_slope, _ = np.polyfit(range(len(flag_data)), flag_data['high'].values, 1)
                low_slope, _ = np.polyfit(range(len(flag_data)), flag_data['low'].values, 1)
                
                if high_slope < -0.001 and low_slope > 0.001:
                    # Check if the ranges are narrowing (converging trendlines)
                    first_half_range = flag_data['high'].iloc[:len(flag_data)//2].max() - flag_data['low'].iloc[:len(flag_data)//2].min()
                    second_half_range = flag_data['high'].iloc[len(flag_data)//2:].max() - flag_data['low'].iloc[len(flag_data)//2:].min()
                    
                    if second_half_range < first_half_range * 0.8:
                        df.loc[df.index[i], 'pennant_bear'] = 1
    
    def _verify_triangle_touches(self, data: pd.DataFrame, peak_x: np.ndarray, peak_y: np.ndarray,
                               trough_x: np.ndarray, trough_y: np.ndarray,
                               upper_slope: float, upper_intercept: float,
                               lower_slope: float, lower_intercept: float) -> bool:
        """
        Verify that price has touched both trendlines multiple times, confirming a valid triangle
        
        Parameters:
        -----------
        data : pd.DataFrame
            Window of price data
        peak_x, peak_y : np.ndarray
            X and Y coordinates of peaks
        trough_x, trough_y : np.ndarray
            X and Y coordinates of troughs
        upper_slope, upper_intercept : float
            Parameters of the upper trendline
        lower_slope, lower_intercept : float
            Parameters of the lower trendline
            
        Returns:
        --------
        bool: True if pattern is valid, False otherwise
        """
        # Count how many times price touches the upper and lower trendlines
        upper_touches = 0
        lower_touches = 0
        
        for i in range(len(data)):
            # Calculate the expected values on the trendlines
            upper_expected = upper_slope * i + upper_intercept
            lower_expected = lower_slope * i + lower_intercept
            
            # Check if price is close to the upper trendline
            if abs(data['high'].iloc[i] - upper_expected) / upper_expected < 0.005:
                upper_touches += 1
            
            # Check if price is close to the lower trendline
            if abs(data['low'].iloc[i] - lower_expected) / lower_expected < 0.005:
                lower_touches += 1
        
        # Valid triangle should have at least 2 touches on each trendline
        return upper_touches >= 2 and lower_touches >= 2
    
    def _verify_channel_touches(self, data: pd.DataFrame, peak_x: np.ndarray, peak_y: np.ndarray,
                              trough_x: np.ndarray, trough_y: np.ndarray,
                              upper_slope: float, upper_intercept: float,
                              lower_slope: float, lower_intercept: float) -> bool:
        """
        Verify that price has touched both trendlines multiple times, confirming a valid channel or wedge
        
        Parameters:
        -----------
        data : pd.DataFrame
            Window of price data
        peak_x, peak_y : np.ndarray
            X and Y coordinates of peaks
        trough_x, trough_y : np.ndarray
            X and Y coordinates of troughs
        upper_slope, upper_intercept : float
            Parameters of the upper trendline
        lower_slope, lower_intercept : float
            Parameters of the lower trendline
            
        Returns:
        --------
        bool: True if pattern is valid, False otherwise
        """
        # Count how many times price touches the upper and lower trendlines
        upper_touches = 0
        lower_touches = 0
        
        for i in range(len(data)):
            # Calculate the expected values on the trendlines
            upper_expected = upper_slope * i + upper_intercept
            lower_expected = lower_slope * i + lower_intercept
            
            # Check if price is close to the upper trendline
            if abs(data['high'].iloc[i] - upper_expected) / upper_expected < 0.01:
                upper_touches += 1
            
            # Check if price is close to the lower trendline
            if abs(data['low'].iloc[i] - lower_expected) / lower_expected < 0.01:
                lower_touches += 1
        
        # Valid channel/wedge should have at least 2 touches on each trendline
        return upper_touches >= 2 and lower_touches >= 2
    
    def get_pattern_summary(self, lookback: int = 5) -> Dict:
        """
        Get a summary of detected patterns in recent data
        
        Parameters:
        -----------
        lookback : int
            Number of periods to look back
            
        Returns:
        --------
        Dict: Summary of detected patterns and their strength
        """
        # First detect all patterns
        df = self.detect_all_patterns()
        
        # Get the recent data
        recent_data = df.iloc[-lookback:].copy()
        
        # Get lists of detected patterns
        candlestick_cols = [col for col in recent_data.columns if col.startswith('cdl_')]
        chart_pattern_cols = ['double_top', 'double_bottom', 'head_shoulders', 'inv_head_shoulders',
                             'triangle_ascending', 'triangle_descending', 'triangle_symmetrical',
                             'channel_up', 'channel_down', 'wedge_rising', 'wedge_falling',
                             'flag_bull', 'flag_bear', 'pennant_bull', 'pennant_bear']
        
        detected_candlesticks = [col for col in candlestick_cols if recent_data[col].any()]
        detected_chart_patterns = [col for col in chart_pattern_cols if recent_data[col].any()]
        
        # Get the latest pattern bias
        latest_bias = recent_data['pattern_bias'].iloc[-1] if 'pattern_bias' in recent_data.columns else 'neutral'
        
        # Format pattern names for readability
        formatted_candlesticks = [col.replace('cdl_', '').replace('_', ' ').title() for col in detected_candlesticks]
        formatted_chart_patterns = [col.replace('_', ' ').title() for col in detected_chart_patterns]
        
        # Categorize patterns by bias
        bullish_patterns = []
        bearish_patterns = []
        
        bullish_candlesticks = ['cdl_hammer', 'cdl_inv_hammer', 'cdl_engulfing_bull', 'cdl_morning_star',
                               'cdl_morning_doji_star', 'cdl_piercing', 'cdl_harami_bull', 'cdl_dragonfly_doji',
                               'cdl_3_white_soldiers', 'cdl_3_inside_up']
        
        bearish_candlesticks = ['cdl_shooting_star', 'cdl_hanging_man', 'cdl_engulfing_bear', 'cdl_evening_star',
                               'cdl_evening_doji_star', 'cdl_dark_cloud_cover', 'cdl_harami_bear', 'cdl_gravestone_doji',
                               'cdl_3_black_crows']
        
        bullish_chart_pats = ['double_bottom', 'inv_head_shoulders', 'triangle_ascending',
                             'channel_up', 'wedge_falling', 'flag_bull', 'pennant_bull']
        
        bearish_chart_pats = ['double_top', 'head_shoulders', 'triangle_descending',
                             'channel_down', 'wedge_rising', 'flag_bear', 'pennant_bear']
        
        for pattern in detected_candlesticks:
            pattern_name = pattern.replace('cdl_', '').replace('_', ' ').title()
            if pattern in bullish_candlesticks:
                bullish_patterns.append(f"{pattern_name} (Candlestick)")
            elif pattern in bearish_candlesticks:
                bearish_patterns.append(f"{pattern_name} (Candlestick)")
        
        for pattern in detected_chart_patterns:
            pattern_name = pattern.replace('_', ' ').title()
            if pattern in bullish_chart_pats:
                bullish_patterns.append(f"{pattern_name} (Chart)")
            elif pattern in bearish_chart_pats:
                bearish_patterns.append(f"{pattern_name} (Chart)")
        
        # Get most recent scores
        latest_scores = {
            'candlestick_score': recent_data['candlestick_pattern_score'].iloc[-1] if 'candlestick_pattern_score' in recent_data.columns else 0,
            'chart_pattern_score': recent_data['chart_pattern_score'].iloc[-1] if 'chart_pattern_score' in recent_data.columns else 0,
            'overall_pattern_score': recent_data['overall_pattern_score'].iloc[-1] if 'overall_pattern_score' in recent_data.columns else 0
        }
        
        return {
            'detected_candlesticks': formatted_candlesticks,
            'detected_chart_patterns': formatted_chart_patterns,
            'bullish_patterns': bullish_patterns,
            'bearish_patterns': bearish_patterns,
            'pattern_bias': latest_bias,
            'pattern_scores': latest_scores,
            'total_patterns': len(bullish_patterns) + len(bearish_patterns)
        }


# Example usage
def analyze_patterns(df: pd.DataFrame) -> pd.DataFrame:
    return PatternEngine(df).detect_all_patterns()

def get_pattern_summary(df: pd.DataFrame, lookback: int = 5) -> Dict:
    return PatternEngine(df).get_pattern_summary(lookback)


if __name__ == "__main__":
    import yfinance as yf

    print("📥 Downloading sample data for NIFTY...")
    data = yf.download("^NSEI", period="3mo", interval="1d", auto_adjust=False)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.columns = [col.lower() for col in data.columns]

    # Analyze patterns
    print("🔍 Analyzing chart patterns...")
    result = analyze_patterns(data)

    # Get pattern summary
    summary = get_pattern_summary(data)
    
    print("\n✅ Pattern Analysis Complete!")
    print(f"Pattern Bias: {summary['pattern_bias']}")
    print(f"Overall Pattern Score: {summary['pattern_scores']['overall_pattern_score']}")
    print(f"Total Patterns Detected: {summary['total_patterns']}")
    
    if summary['bullish_patterns']:
        print("\n📈 Bullish Patterns:")
        for pattern in summary['bullish_patterns']:
            print(f"  - {pattern}")
    
    if summary['bearish_patterns']:
        print("\n📉 Bearish Patterns:")
        for pattern in summary['bearish_patterns']:
            print(f"  - {pattern}")
    
    # Save the results
    result.to_csv("pattern_analysis.csv")
    print("\n📁 Full analysis saved to pattern_analysis.csv")