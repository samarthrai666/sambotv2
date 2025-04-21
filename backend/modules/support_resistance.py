import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any

def get_support_resistance(data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, List[float]]:
    """
    Identify support and resistance levels from price data
    
    Parameters:
    -----------
    data : pd.DataFrame or dict
        Either a DataFrame with OHLCV data or a dictionary with 'candles' key
        
    Returns:
    --------
    dict: Dictionary with support and resistance levels
    """
    try:
        # Convert data to DataFrame if it's not already
        if isinstance(data, dict) and 'candles' in data:
            candles = data['candles']
            if not candles or len(candles) < 10:  # Need sufficient history
                return {
                    "support": [],
                    "resistance": [],
                    "error": "Insufficient data for support/resistance analysis"
                }
            
            # Convert candles to DataFrame
            df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            return {
                "support": [],
                "resistance": [],
                "error": "Invalid data format for support/resistance analysis"
            }
        
        # Check if we have enough data
        if df.empty or len(df) < 10:
            return {
                "support": [],
                "resistance": [],
                "error": "Insufficient data points for analysis"
            }
        
        # Simple method: Find local minima and maxima
        # More sophisticated methods would use fractal analysis, market structure, etc.
        
        # Use rolling windows to identify local extrema
        window_size = min(10, len(df) // 3)  # Use appropriate window size
        
        # Find local minima (support)
        rolling_min = df['low'].rolling(window=window_size, center=True).min()
        is_local_min = (df['low'] == rolling_min) & (df['low'].shift(window_size // 2) != df['low'])
        
        # Find local maxima (resistance)
        rolling_max = df['high'].rolling(window=window_size, center=True).max()
        is_local_max = (df['high'] == rolling_max) & (df['high'].shift(window_size // 2) != df['high'])
        
        # Extract support and resistance levels
        support_levels = df.loc[is_local_min, 'low'].tolist()
        resistance_levels = df.loc[is_local_max, 'high'].tolist()
        
        # Remove duplicates and sort
        support_levels = sorted(list(set([round(x, 2) for x in support_levels])))
        resistance_levels = sorted(list(set([round(x, 2) for x in resistance_levels])))
        
        # Cluster nearby levels (optional)
        support_levels = cluster_nearby_levels(support_levels)
        resistance_levels = cluster_nearby_levels(resistance_levels)
        
        return {
            "support": support_levels,
            "resistance": resistance_levels,
            "current_price": float(df['close'].iloc[-1]),
            "nearest_support": find_nearest_level(support_levels, float(df['close'].iloc[-1]), below=True),
            "nearest_resistance": find_nearest_level(resistance_levels, float(df['close'].iloc[-1]), below=False)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "support": [],
            "resistance": [],
            "error": str(e)
        }

def cluster_nearby_levels(levels: List[float], threshold_pct: float = 0.5) -> List[float]:
    """
    Cluster nearby price levels to avoid redundancy
    
    Parameters:
    -----------
    levels : List[float]
        List of price levels to cluster
    threshold_pct : float
        Percentage threshold for clustering (default 0.5%)
        
    Returns:
    --------
    List[float]: Clustered price levels
    """
    if not levels:
        return []
    
    # Sort levels
    sorted_levels = sorted(levels)
    
    # Initialize clusters with the first level
    clusters = [[sorted_levels[0]]]
    
    # Cluster nearby levels
    for level in sorted_levels[1:]:
        # Calculate percentage difference with the last cluster's average
        last_cluster_avg = sum(clusters[-1]) / len(clusters[-1])
        pct_diff = abs(level - last_cluster_avg) / last_cluster_avg * 100
        
        # If close enough, add to the last cluster
        if pct_diff <= threshold_pct:
            clusters[-1].append(level)
        # Otherwise, create a new cluster
        else:
            clusters.append([level])
    
    # Calculate the average of each cluster
    clustered_levels = [sum(cluster) / len(cluster) for cluster in clusters]
    
    return clustered_levels

def find_nearest_level(levels: List[float], price: float, below: bool = True) -> float:
    """
    Find the nearest support/resistance level to the current price
    
    Parameters:
    -----------
    levels : List[float]
        List of price levels
    price : float
        Current price
    below : bool
        If True, find the nearest level below the price,
        otherwise find the nearest level above
        
    Returns:
    --------
    float: Nearest level (or price * 0.99 or price * 1.01 if no levels found)
    """
    if not levels:
        return price * 0.99 if below else price * 1.01
    
    if below:
        # Levels below the price
        below_levels = [level for level in levels if level < price]
        if below_levels:
            return max(below_levels)  # Highest level below price
        return price * 0.99  # Fallback if no levels below
    else:
        # Levels above the price
        above_levels = [level for level in levels if level > price]
        if above_levels:
            return min(above_levels)  # Lowest level above price
        return price * 1.01  # Fallback if no levels above