import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class OptionChainAnalyzer:
    """
    Advanced AI-powered option chain analyzer for grid trading strategies.
    Extracts key insights from options data to identify optimal grid levels.
    """
    
    def __init__(self, option_chain_data: pd.DataFrame, spot_price: float, 
                 risk_free_rate: float = 0.05, analysis_date: Optional[datetime] = None):
        """
        Initialize the option chain analyzer
        
        Parameters:
        -----------
        option_chain_data : pd.DataFrame
            DataFrame containing option chain data with columns:
            strike, call_price, put_price, call_oi, put_oi, call_volume, put_volume,
            call_iv, put_iv, expiry_date
        spot_price : float
            Current spot price of the underlying
        risk_free_rate : float
            Risk-free interest rate (annual)
        analysis_date : datetime, optional
            Date of analysis, defaults to current date
        """
        self.data = option_chain_data.copy()
        self.spot_price = spot_price
        self.risk_free_rate = risk_free_rate
        self.analysis_date = analysis_date or datetime.now()
        
        # Validate input data
        self._validate_data()
        
        # Prepare data
        self._prepare_data()
        
        # Calculate derived metrics
        self._calculate_derived_metrics()
        
        # Initialize analysis result containers
        self.max_pain_point = None
        self.iv_skew_analysis = None
        self.dealer_gamma_exposure = None
        self.support_resistance_levels = None
        self.put_call_ratio_analysis = None
        self.implied_range = None
        self.market_sentiment_score = None
        self.strike_specific_greeks = None
        self.grid_levels = None
    
    def _validate_data(self):
        """Validate input data structure"""
        required_columns = ['strike', 'call_price', 'put_price']
        missing = [col for col in required_columns if col not in self.data.columns]
        
        if missing:
            raise ValueError(f"Option chain data missing required columns: {', '.join(missing)}")
    
    def _prepare_data(self):
        """Prepare and clean the data for analysis"""
        # Sort by strike
        self.data = self.data.sort_values('strike').reset_index(drop=True)
        
        # Calculate time to expiration in years
        if 'expiry_date' in self.data.columns:
            self.data['dte'] = (pd.to_datetime(self.data['expiry_date']) - pd.to_datetime(self.analysis_date)).dt.days
            self.data['time_to_expiry'] = self.data['dte'] / 365
            
            # Filter for single expiry if multiple are present
            if self.data['time_to_expiry'].nunique() > 1:
                # Use the closest expiry by default
                closest_expiry = self.data['time_to_expiry'].min()
                self.data = self.data[self.data['time_to_expiry'] == closest_expiry].copy()
        else:
            # If no expiry date, assume standard 30-day options
            self.data['time_to_expiry'] = 30/365
        
        # Fill missing values with calculated values where possible
        self._fill_missing_values()
    
    def _fill_missing_values(self):
        """Fill missing values in the option chain data"""
        # Fill missing IVs using Black-Scholes if prices are available
        if 'call_iv' not in self.data.columns or self.data['call_iv'].isnull().any():
            self.data['call_iv'] = self.data.apply(
                lambda row: self._calculate_implied_volatility(
                    option_price=row['call_price'],
                    strike=row['strike'],
                    time_to_expiry=row['time_to_expiry'],
                    option_type='call'
                ) if pd.notnull(row['call_price']) else np.nan,
                axis=1
            )
        
        if 'put_iv' not in self.data.columns or self.data['put_iv'].isnull().any():
            self.data['put_iv'] = self.data.apply(
                lambda row: self._calculate_implied_volatility(
                    option_price=row['put_price'],
                    strike=row['strike'],
                    time_to_expiry=row['time_to_expiry'],
                    option_type='put'
                ) if pd.notnull(row['put_price']) else np.nan,
                axis=1
            )
        
        # Ensure OI and volume columns exist
        for col in ['call_oi', 'put_oi', 'call_volume', 'put_volume']:
            if col not in self.data.columns:
                self.data[col] = 0
    
    def _calculate_derived_metrics(self):
        """Calculate additional derived metrics for analysis"""
        # Calculate moneyness
        self.data['moneyness'] = self.data['strike'] / self.spot_price
        
        # Average IV
        self.data['avg_iv'] = (self.data['call_iv'] + self.data['put_iv']) / 2
        
        # Calculate call/put ratio
        self.data['cp_oi_ratio'] = self.data['call_oi'] / self.data['put_oi'].replace(0, 1)
        self.data['cp_volume_ratio'] = self.data['call_volume'] / self.data['put_volume'].replace(0, 1)
        
        # Calculate intrinsic and extrinsic values
        self.data['call_intrinsic'] = np.maximum(0, self.spot_price - self.data['strike'])
        self.data['put_intrinsic'] = np.maximum(0, self.data['strike'] - self.spot_price)
        self.data['call_extrinsic'] = self.data['call_price'] - self.data['call_intrinsic']
        self.data['put_extrinsic'] = self.data['put_price'] - self.data['put_intrinsic']
        
        # Calculate composite metrics
        self.data['oi_weight'] = (self.data['call_oi'] + self.data['put_oi']) / (self.data['call_oi'] + self.data['put_oi']).sum()
        self.data['volume_weight'] = (self.data['call_volume'] + self.data['put_volume']) / (self.data['call_volume'] + self.data['put_volume']).sum()
        
        # Calculate option Greeks
        self._calculate_greeks()
    
    def _calculate_greeks(self):
        """Calculate option Greeks for the chain"""
        # Calculate Delta
        self.data['call_delta'] = self.data.apply(
            lambda row: self._calculate_delta(
                strike=row['strike'],
                time_to_expiry=row['time_to_expiry'],
                volatility=row['call_iv'],
                option_type='call'
            ),
            axis=1
        )
        
        self.data['put_delta'] = self.data.apply(
            lambda row: self._calculate_delta(
                strike=row['strike'],
                time_to_expiry=row['time_to_expiry'],
                volatility=row['put_iv'],
                option_type='put'
            ),
            axis=1
        )
        
        # Calculate Gamma (same for calls and puts)
        self.data['gamma'] = self.data.apply(
            lambda row: self._calculate_gamma(
                strike=row['strike'],
                time_to_expiry=row['time_to_expiry'],
                volatility=row['avg_iv']
            ),
            axis=1
        )
        
        # Calculate Theta
        self.data['call_theta'] = self.data.apply(
            lambda row: self._calculate_theta(
                strike=row['strike'],
                time_to_expiry=row['time_to_expiry'],
                volatility=row['call_iv'],
                option_type='call'
            ),
            axis=1
        )
        
        self.data['put_theta'] = self.data.apply(
            lambda row: self._calculate_theta(
                strike=row['strike'],
                time_to_expiry=row['time_to_expiry'],
                volatility=row['put_iv'],
                option_type='put'
            ),
            axis=1
        )
        
        # Calculate Vega (same for calls and puts)
        self.data['vega'] = self.data.apply(
            lambda row: self._calculate_vega(
                strike=row['strike'],
                time_to_expiry=row['time_to_expiry'],
                volatility=row['avg_iv']
            ),
            axis=1
        )
        
        # Calculate dollar gamma exposure
        self.data['dollar_gamma'] = self.data['gamma'] * self.data['oi_weight'] * self.spot_price * self.spot_price * 0.01
    
    def _calculate_implied_volatility(self, option_price: float, strike: float, 
                                     time_to_expiry: float, option_type: str) -> float:
        """
        Calculate implied volatility using Black-Scholes model and optimization
        
        Parameters:
        -----------
        option_price : float
            Market price of the option
        strike : float
            Strike price
        time_to_expiry : float
            Time to expiration in years
        option_type : str
            Type of option ('call' or 'put')
            
        Returns:
        --------
        float: Implied volatility
        """
        if option_price <= 0 or strike <= 0 or time_to_expiry <= 0:
            return np.nan
        
        # Define the objective function to minimize
        def objective(vol):
            if option_type.lower() == 'call':
                model_price = self._calculate_bsm_call(strike, time_to_expiry, vol)
            else:
                model_price = self._calculate_bsm_put(strike, time_to_expiry, vol)
            return (model_price - option_price) ** 2
        
        try:
            # Use optimization to find the implied volatility
            result = minimize(objective, x0=0.3, bounds=[(0.001, 5.0)], method='L-BFGS-B')
            if result.success:
                return result.x[0]
            else:
                return np.nan
        except:
            return np.nan
    
    def _calculate_bsm_call(self, strike: float, time_to_expiry: float, volatility: float) -> float:
        """
        Calculate call option price using Black-Scholes model
        
        Parameters:
        -----------
        strike : float
            Strike price
        time_to_expiry : float
            Time to expiration in years
        volatility : float
            Implied volatility
            
        Returns:
        --------
        float: Call option price
        """
        if time_to_expiry <= 0 or volatility <= 0:
            return max(0, self.spot_price - strike)
        
        d1 = (np.log(self.spot_price / strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        return self.spot_price * stats.norm.cdf(d1) - strike * np.exp(-self.risk_free_rate * time_to_expiry) * stats.norm.cdf(d2)
    
    def _calculate_bsm_put(self, strike: float, time_to_expiry: float, volatility: float) -> float:
        """
        Calculate put option price using Black-Scholes model
        
        Parameters:
        -----------
        strike : float
            Strike price
        time_to_expiry : float
            Time to expiration in years
        volatility : float
            Implied volatility
            
        Returns:
        --------
        float: Put option price
        """
        if time_to_expiry <= 0 or volatility <= 0:
            return max(0, strike - self.spot_price)
        
        d1 = (np.log(self.spot_price / strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        return strike * np.exp(-self.risk_free_rate * time_to_expiry) * stats.norm.cdf(-d2) - self.spot_price * stats.norm.cdf(-d1)
    
    def _calculate_delta(self, strike: float, time_to_expiry: float, volatility: float, option_type: str) -> float:
        """Calculate option delta"""
        if time_to_expiry <= 0 or volatility <= 0:
            return 1.0 if option_type == 'call' and self.spot_price > strike else (0.0 if option_type == 'call' else 1.0)
        
        d1 = (np.log(self.spot_price / strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        
        if option_type == 'call':
            return stats.norm.cdf(d1)
        else:
            return stats.norm.cdf(d1) - 1
    
    def _calculate_gamma(self, strike: float, time_to_expiry: float, volatility: float) -> float:
        """Calculate option gamma"""
        if time_to_expiry <= 0 or volatility <= 0:
            return 0.0
        
        d1 = (np.log(self.spot_price / strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        
        return stats.norm.pdf(d1) / (self.spot_price * volatility * np.sqrt(time_to_expiry))
    
    def _calculate_theta(self, strike: float, time_to_expiry: float, volatility: float, option_type: str) -> float:
        """Calculate option theta"""
        if time_to_expiry <= 0 or volatility <= 0:
            return 0.0
        
        d1 = (np.log(self.spot_price / strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        common_term = -(self.spot_price * stats.norm.pdf(d1) * volatility) / (2 * np.sqrt(time_to_expiry))
        
        if option_type == 'call':
            return common_term - self.risk_free_rate * strike * np.exp(-self.risk_free_rate * time_to_expiry) * stats.norm.cdf(d2)
        else:
            return common_term + self.risk_free_rate * strike * np.exp(-self.risk_free_rate * time_to_expiry) * stats.norm.cdf(-d2)
    
    def _calculate_vega(self, strike: float, time_to_expiry: float, volatility: float) -> float:
        """Calculate option vega"""
        if time_to_expiry <= 0 or volatility <= 0:
            return 0.0
        
        d1 = (np.log(self.spot_price / strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        
        return self.spot_price * stats.norm.pdf(d1) * np.sqrt(time_to_expiry) / 100  # Divided by 100 for 1% change
    
    def analyze_max_pain(self) -> Dict:
        """
        Calculate the max pain point (strike where option writers have minimum pain)
        
        Returns:
        --------
        Dict: Max pain analysis with strike, impact and interpretation
        """
        if 'call_oi' not in self.data.columns or 'put_oi' not in self.data.columns:
            max_pain = self.spot_price
            max_pain_impact = "Neutral"
            max_pain_deviation = 0
        else:
            strikes = self.data['strike'].values
            call_oi = self.data['call_oi'].values
            put_oi = self.data['put_oi'].values
            
            # Calculate pain for option writers at each strike
            pain_at_strike = []
            
            for test_price in strikes:
                # Calculate call writer pain
                call_pain = sum(call_oi[i] * max(0, test_price - strikes[i]) for i in range(len(strikes)))
                
                # Calculate put writer pain
                put_pain = sum(put_oi[i] * max(0, strikes[i] - test_price) for i in range(len(strikes)))
                
                # Total pain
                total_pain = call_pain + put_pain
                pain_at_strike.append(total_pain)
            
            # Find strike with minimum pain
            idx_min_pain = np.argmin(pain_at_strike)
            max_pain = strikes[idx_min_pain]
            
            # Calculate deviation and impact
            max_pain_deviation = (max_pain / self.spot_price - 1) * 100
            
            # Determine expected impact
            if abs(max_pain_deviation) < 0.5:
                max_pain_impact = "Neutral - Spot price aligned with max pain"
            elif max_pain_deviation > 2:
                max_pain_impact = "Bullish - Max pain above spot, potential upward magnet"
            elif max_pain_deviation < -2:
                max_pain_impact = "Bearish - Max pain below spot, potential downward magnet"
            elif max_pain_deviation > 0:
                max_pain_impact = "Slightly Bullish - Max pain slightly above spot"
            else:
                max_pain_impact = "Slightly Bearish - Max pain slightly below spot"
        
        self.max_pain_point = {
            'price': max_pain,
            'deviation_pct': max_pain_deviation,
            'impact': max_pain_impact
        }
        
        return self.max_pain_point
    
    def analyze_iv_skew(self) -> Dict:
        """
        Analyze IV skew (put vs call premium) for market sentiment
        
        Returns:
        --------
        Dict: IV skew analysis with metrics and interpretation
        """
        if 'moneyness' not in self.data.columns or 'call_iv' not in self.data.columns:
            return {
                'skew_25delta': 0,
                'skew_ratio': 1,
                'atm_iv': 0,
                'interpretation': "Insufficient data for IV skew analysis"
            }
        
        # Sort by moneyness
        sorted_data = self.data.sort_values('moneyness').copy()
        
        # Find ATM options (closest to moneyness = 1)
        atm_idx = abs(sorted_data['moneyness'] - 1).idxmin()
        atm_iv = sorted_data.loc[atm_idx, 'avg_iv']
        
        # Find 25-delta options (approximately moneyness 0.95 and 1.05)
        try:
            # For put IV (OTM puts, approximately 25-delta)
            put_idx = abs(sorted_data['moneyness'] - 0.95).idxmin()
            otm_put_iv = sorted_data.loc[put_idx, 'put_iv']
            
            # For call IV (OTM calls, approximately 25-delta)
            call_idx = abs(sorted_data['moneyness'] - 1.05).idxmin()
            otm_call_iv = sorted_data.loc[call_idx, 'call_iv']
            
            # Calculate 25-delta skew (put IV - call IV)
            skew_25delta = otm_put_iv - otm_call_iv
            
            # Calculate skew ratio
            skew_ratio = otm_put_iv / otm_call_iv
            
            # Interpret skew
            if skew_ratio > 1.15:
                skew_severity = "Strong"
                skew_type = "Put"
                interpretation = "Bearish - Significantly higher put premiums indicate fear of downside"
            elif skew_ratio > 1.05:
                skew_severity = "Moderate"
                skew_type = "Put"
                interpretation = "Slightly Bearish - Moderately higher put premiums"
            elif skew_ratio < 0.85:
                skew_severity = "Strong"
                skew_type = "Call"
                interpretation = "Bullish - Significantly higher call premiums indicate upside excitement"
            elif skew_ratio < 0.95:
                skew_severity = "Moderate"
                skew_type = "Call"
                interpretation = "Slightly Bullish - Moderately higher call premiums"
            else:
                skew_severity = "Neutral"
                skew_type = "Balanced"
                interpretation = "Neutral - Balanced premiums between calls and puts"
            
            # Additional Insights
            if skew_ratio > 1.3:
                hedging_insight = "Extremely high put skew can signal potential reversal (contrarian)"
            elif skew_ratio < 0.7:
                hedging_insight = "Extremely high call skew can signal potential reversal (contrarian)"
            else:
                hedging_insight = "Normal skew levels, no contrarian signal"
            
        except:
            skew_25delta = 0
            skew_ratio = 1
            skew_severity = "Unknown"
            skew_type = "Unknown"
            interpretation = "Could not calculate IV skew"
            hedging_insight = "N/A"
        
        self.iv_skew_analysis = {
            'skew_25delta': skew_25delta,
            'skew_ratio': skew_ratio,
            'atm_iv': atm_iv,
            'skew_severity': skew_severity,
            'skew_type': skew_type,
            'interpretation': interpretation,
            'hedging_insight': hedging_insight
        }
        
        return self.iv_skew_analysis
    
    def analyze_dealer_gamma(self) -> Dict:
        """
        Analyze dealer gamma exposure profile for market stability
        
        Returns:
        --------
        Dict: Gamma exposure analysis with metrics and interpretation
        """
        if 'gamma' not in self.data.columns or 'call_oi' not in self.data.columns:
            return {
                'net_gamma': 0,
                'interpretation': "Insufficient data for gamma analysis"
            }
        
        # Calculate call and put gamma exposure
        self.data['call_gamma_exposure'] = self.data['gamma'] * self.data['call_oi'] * self.spot_price * self.spot_price * 0.01
        self.data['put_gamma_exposure'] = self.data['gamma'] * self.data['put_oi'] * self.spot_price * self.spot_price * 0.01
        
        # Sum up gamma exposures
        net_gamma_exposure = self.data['call_gamma_exposure'].sum() - self.data['put_gamma_exposure'].sum()
        total_gamma_exposure = self.data['call_gamma_exposure'].sum() + self.data['put_gamma_exposure'].sum()
        
        # Normalize gamma by spot price for comparative measure
        normalized_net_gamma = net_gamma_exposure / (self.spot_price * 10000)
        
        # Identify highest gamma strikes (potential price magnets)
        self.data['total_gamma_at_strike'] = self.data['call_gamma_exposure'] + self.data['put_gamma_exposure']
        top_gamma_strikes = self.data.nlargest(3, 'total_gamma_at_strike')[['strike', 'total_gamma_at_strike']]
        
        # Evaluate gamma implications
        if normalized_net_gamma > 0.3:
            gamma_impact = "Strong Positive Gamma"
            stability = "High Stability"
            hedging_behavior = "Market makers will sell into rallies and buy dips, dampening volatility"
            volatility_forecast = "Lower expected volatility, price likely to consolidate"
        elif normalized_net_gamma > 0.1:
            gamma_impact = "Moderate Positive Gamma"
            stability = "Moderate Stability"
            hedging_behavior = "Some stabilizing hedging flow expected on price moves"
            volatility_forecast = "Moderate volatility dampening effect"
        elif normalized_net_gamma < -0.3:
            gamma_impact = "Strong Negative Gamma"
            stability = "High Instability"
            hedging_behavior = "Market makers will buy into rallies and sell into dips, amplifying volatility"
            volatility_forecast = "Higher expected volatility, potential for accelerated moves"
        elif normalized_net_gamma < -0.1:
            gamma_impact = "Moderate Negative Gamma"
            stability = "Moderate Instability"
            hedging_behavior = "Some destabilizing hedging flow expected on price moves"
            volatility_forecast = "Moderate volatility enhancing effect"
        else:
            gamma_impact = "Neutral Gamma"
            stability = "Neutral Stability"
            hedging_behavior = "Limited hedging impact expected"
            volatility_forecast = "Normal volatility conditions"
        
        # Calculate gamma concentration to identify potential reversal points
        gamma_concentration = []
        for _, row in top_gamma_strikes.iterrows():
            strike = row['strike']
            concentration = row['total_gamma_at_strike'] / total_gamma_exposure * 100 if total_gamma_exposure > 0 else 0
            gamma_concentration.append({
                'strike': strike,
                'concentration_pct': concentration,
                'deviation_from_spot_pct': (strike / self.spot_price - 1) * 100
            })
        
        self.dealer_gamma_exposure = {
            'net_gamma': net_gamma_exposure,
            'normalized_net_gamma': normalized_net_gamma,
            'gamma_impact': gamma_impact,
            'stability': stability,
            'hedging_behavior': hedging_behavior,
            'volatility_forecast': volatility_forecast,
            'gamma_concentration': gamma_concentration
        }
        
        return self.dealer_gamma_exposure
    
    def analyze_support_resistance(self, bandwidth: float = 0.02) -> List[Dict]:
        """
        Identify support and resistance levels from option data
        
        Parameters:
        -----------
        bandwidth : float
            Relative bandwidth for clustering nearby levels
            
        Returns:
        --------
        List[Dict]: List of identified support/resistance levels with metadata
        """
        # Calculate support/resistance levels from options data
        levels = []
        
        # 1. High OI strikes
        if 'call_oi' in self.data.columns and 'put_oi' in self.data.columns:
            oi_threshold_call = self.data['call_oi'].max() * 0.7
            high_call_oi = self.data[self.data['call_oi'] > oi_threshold_call]['strike'].tolist()
            
            oi_threshold_put = self.data['put_oi'].max() * 0.7
            high_put_oi = self.data[self.data['put_oi'] > oi_threshold_put]['strike'].tolist()
            
            # Add levels
            for strike in high_call_oi:
                levels.append({
                    'strike': strike,
                    'type': 'resistance',
                    'source': 'call_oi',
                    'strength': 0.7
                })
            
            for strike in high_put_oi:
                levels.append({
                    'strike': strike,
                    'type': 'support',
                    'source': 'put_oi',
                    'strength': 0.7
                })
        
        # 2. High Gamma strikes
        if 'gamma' in self.data.columns:
            gamma_threshold = self.data['gamma'].max() * 0.6
            high_gamma = self.data[self.data['gamma'] > gamma_threshold]['strike'].tolist()
            
            for strike in high_gamma:
                levels.append({
                    'strike': strike,
                    'type': 'pivot',
                    'source': 'gamma',
                    'strength': 0.8
                })
        
        # 3. Zero-delta strikes (ATM)
        if 'call_delta' in self.data.columns:
            atm_index = abs(self.data['call_delta'] - 0.5).idxmin()
            atm_strike = self.data.iloc[atm_index]['strike']
            
            levels.append({
                'strike': atm_strike,
                'type': 'pivot',
                'source': 'delta',
                'strength': 0.9
            })
        
        # 4. Add current spot price
        levels.append({
            'strike': self.spot_price,
            'type': 'current',
            'source': 'market',
            'strength': 1.0
        })
        
        # 5. Add max pain point if calculated
        if hasattr(self, 'max_pain_point') and self.max_pain_point:
            levels.append({
                'strike': self.max_pain_point['price'],
                'type': 'magnet',
                'source': 'max_pain',
                'strength': 0.85
            })
        
        # Cluster nearby levels
        bandwidth_value = self.spot_price * bandwidth
        clustered_levels = []
        
        # Sort by strike
        sorted_levels = sorted(levels, key=lambda x: x['strike'])
        
        i = 0
        while i < len(sorted_levels):
            cluster = [sorted_levels[i]]
            j = i + 1
            
            # Find all levels within bandwidth
            while j < len(sorted_levels) and abs(sorted_levels[j]['strike'] - sorted_levels[i]['strike']) <= bandwidth_value:
                cluster.append(sorted_levels[j])
                j += 1
            
            # Combine cluster into a single level
            avg_strike = sum(level['strike'] for level in cluster) / len(cluster)
            max_strength = max(level['strength'] for level in cluster)
            sources = [level['source'] for level in cluster]
            types = [level['type'] for level in cluster]
            
            # Determine dominant type
            type_counts = {}
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1
            
            dominant_type = max(type_counts.items(), key=lambda x: x[1])[0]
            
            # Calculate confirmation strength based on cluster size
            confirmation_strength = min(len(cluster) / 3, 1.0)
            
            clustered_levels.append({
                'strike': avg_strike,
                'type': dominant_type,
                'sources': sources,
                'strength': max_strength * (0.7 + 0.3 * confirmation_strength),
                'deviation_from_spot_pct': (avg_strike / self.spot_price - 1) * 100
            })
            
            i = j
        
        # Sort by price
        clustered_levels = sorted(clustered_levels, key=lambda x: x['strike'])
        
        # Categorize levels as support or resistance based on spot price
        for level in clustered_levels:
            if level['strike'] < self.spot_price:
                if level['type'] not in ['support', 'magnet']:
                    level['type'] = 'support'
            elif level['strike'] > self.spot_price:
                if level['type'] not in ['resistance', 'magnet']:
                    level['type'] = 'resistance'
            else:
                level['type'] = 'current_price'
        
        self.support_resistance_levels = clustered_levels
        return clustered_levels
    
    def analyze_put_call_ratio(self) -> Dict:
        """
        Analyze put-call ratio for contrarian signals
        
        Returns:
        --------
        Dict: Put-call ratio analysis with metrics and interpretation
        """
        if 'call_oi' not in self.data.columns or 'put_oi' not in self.data.columns:
            return {
                'pcr_oi': 1.0,
                'pcr_volume': 1.0,
                'interpretation': "Insufficient data for PCR analysis"
            }
        
        # Calculate PCR (Put-Call Ratio)
        pcr_oi = self.data['put_oi'].sum() / max(1, self.data['call_oi'].sum())
        
        if 'call_volume' in self.data.columns and 'put_volume' in self.data.columns:
            pcr_volume = self.data['put_volume'].sum() / max(1, self.data['call_volume'].sum())
        else:
            pcr_volume = pcr_oi
        
        # Interpret PCR values
        # OI PCR interpretation (more stable, relevant for position sentiment)
        if pcr_oi > 2.0:
            oi_interpretation = "Extremely Bearish Positioning (Bullish Contrarian Signal)"
            oi_sentiment = "Bearish"
            oi_contrarian = "Strong Bullish"
        elif pcr_oi > 1.5:
            oi_interpretation = "Bearish Positioning (Moderate Bullish Contrarian Signal)"
            oi_sentiment = "Bearish"
            oi_contrarian = "Moderate Bullish"
        elif pcr_oi > 1.2:
            oi_interpretation = "Slightly Bearish Positioning"
            oi_sentiment = "Slightly Bearish"
            oi_contrarian = "Slightly Bullish"
        elif pcr_oi < 0.5:
            oi_interpretation = "Extremely Bullish Positioning (Bearish Contrarian Signal)"
            oi_sentiment = "Bullish"
            oi_contrarian = "Strong Bearish"
        elif pcr_oi < 0.7:
            oi_interpretation = "Bullish Positioning (Moderate Bearish Contrarian Signal)"
            oi_sentiment = "Bullish"
            oi_contrarian = "Moderate Bearish"
        elif pcr_oi < 0.8:
            oi_interpretation = "Slightly Bullish Positioning"
            oi_sentiment = "Slightly Bullish"
            oi_contrarian = "Slightly Bearish"
        else:
            oi_interpretation = "Neutral Positioning"
            oi_sentiment = "Neutral"
            oi_contrarian = "Neutral"
        
        # Volume PCR interpretation (more reactive, relevant for day's sentiment)
        if pcr_volume > 2.5:
            volume_interpretation = "Panic Buying of Puts (Strong Bullish Contrarian Signal)"
            volume_sentiment = "Bearish"
            volume_contrarian = "Strong Bullish"
        elif pcr_volume > 1.8:
            volume_interpretation = "Fearful Buying of Puts (Bullish Contrarian Signal)"
            volume_sentiment = "Bearish"
            volume_contrarian = "Moderate Bullish"
        elif pcr_volume > 1.3:
            volume_interpretation = "Cautious Sentiment (Slight Bullish Contrarian Signal)"
            volume_sentiment = "Slightly Bearish"
            volume_contrarian = "Slightly Bullish"
        elif pcr_volume < 0.4:
            volume_interpretation = "Frenzy Call Buying (Strong Bearish Contrarian Signal)"
            volume_sentiment = "Bullish"
            volume_contrarian = "Strong Bearish"
        elif pcr_volume < 0.6:
            volume_interpretation = "Aggressive Call Buying (Bearish Contrarian Signal)"
            volume_sentiment = "Bullish"
            volume_contrarian = "Moderate Bearish"
        elif pcr_volume < 0.8:
            volume_interpretation = "Optimistic Sentiment (Slight Bearish Contrarian Signal)"
            volume_sentiment = "Slightly Bullish"
            volume_contrarian = "Slightly Bearish"
        else:
            volume_interpretation = "Balanced Trading Activity"
            volume_sentiment = "Neutral"
            volume_contrarian = "Neutral"
        
        self.put_call_ratio_analysis = {
            'pcr_oi': pcr_oi,
            'pcr_volume': pcr_volume,
            'oi_interpretation': oi_interpretation,
            'oi_sentiment': oi_sentiment,
            'oi_contrarian': oi_contrarian,
            'volume_interpretation': volume_interpretation,
            'volume_sentiment': volume_sentiment,
            'volume_contrarian': volume_contrarian,
            'consolidated_sentiment': volume_sentiment if abs(pcr_volume - 1) > abs(pcr_oi - 1) else oi_sentiment
        }
        
        return self.put_call_ratio_analysis
    
    def analyze_implied_range(self, confidence: float = 0.68) -> Dict:
        """
        Calculate the implied price range based on option IVs
        
        Parameters:
        -----------
        confidence : float
            Confidence level (e.g., 0.68 for 1-sigma, 0.95 for 2-sigma)
            
        Returns:
        --------
        Dict: Implied range analysis with bounds and interpretation
        """
        # Calculate average IV across the chain, weighted by OI
        if 'avg_iv' not in self.data.columns or 'oi_weight' not in self.data.columns:
            weighted_iv = 0.2  # Default 20% IV if not available
        else:
            weighted_iv = np.sum(self.data['avg_iv'] * self.data['oi_weight'])
        
        # Get time to expiry (in years)
        time_to_expiry = self.data['time_to_expiry'].iloc[0]
        
        # Calculate z-score for the given confidence level
        z_score = stats.norm.ppf((1 + confidence) / 2)
        
        # Calculate implied range
        price_change_factor = np.exp(z_score * weighted_iv * np.sqrt(time_to_expiry))
        
        lower_bound = self.spot_price / price_change_factor
        upper_bound = self.spot_price * price_change_factor
        
        # Calculate range width
        range_width_pct = (upper_bound - lower_bound) / self.spot_price * 100
        
        # Interpret the range
        if range_width_pct < 3:
            range_interpretation = "Very Narrow Range - Market expects minimal movement"
        elif range_width_pct < 6:
            range_interpretation = "Narrow Range - Market expects below-average movement"
        elif range_width_pct < 10:
            range_interpretation = "Average Range - Market expects normal movement"
        elif range_width_pct < 15:
            range_interpretation = "Wide Range - Market expects significant movement"
        else:
            range_interpretation = "Very Wide Range - Market expects extreme movement"
        
        # Calculate probability of staying within different ranges
        one_sigma_prob = stats.norm.cdf(1) - stats.norm.cdf(-1)  # ~68%
        two_sigma_prob = stats.norm.cdf(2) - stats.norm.cdf(-2)  # ~95%
        
        # Calculate range for popular confidence levels
        one_sigma_factor = np.exp(1 * weighted_iv * np.sqrt(time_to_expiry))
        two_sigma_factor = np.exp(2 * weighted_iv * np.sqrt(time_to_expiry))
        
        one_sigma_range = (self.spot_price / one_sigma_factor, self.spot_price * one_sigma_factor)
        two_sigma_range = (self.spot_price / two_sigma_factor, self.spot_price * two_sigma_factor)
        
        self.implied_range = {
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'range_width_pct': range_width_pct,
            'interpretation': range_interpretation,
            'confidence_level': confidence,
            'implied_volatility': weighted_iv,
            'time_to_expiry_days': time_to_expiry * 365,
            'one_sigma_range': one_sigma_range,
            'two_sigma_range': two_sigma_range,
            'one_sigma_probability': one_sigma_prob * 100,
            'two_sigma_probability': two_sigma_prob * 100
        }
        
        return self.implied_range
    
    def calculate_market_sentiment(self) -> Dict:
        """
        Calculate comprehensive market sentiment score
        
        Returns:
        --------
        Dict: Market sentiment analysis with score and interpretation
        """
        # Make sure all component analyses have been performed
        if not hasattr(self, 'put_call_ratio_analysis') or not self.put_call_ratio_analysis:
            self.analyze_put_call_ratio()
        
        if not hasattr(self, 'iv_skew_analysis') or not self.iv_skew_analysis:
            self.analyze_iv_skew()
        
        if not hasattr(self, 'max_pain_point') or not self.max_pain_point:
            self.analyze_max_pain()
        
        if not hasattr(self, 'dealer_gamma_exposure') or not self.dealer_gamma_exposure:
            self.analyze_dealer_gamma()
        
        # Initialize sentiment components
        sentiment_components = []
        
        # 1. PCR OI component (0-20 points)
        pcr_oi = self.put_call_ratio_analysis.get('pcr_oi', 1.0)
        if pcr_oi > 1.0:
            # Bullish signal (contrarian)
            pcr_oi_score = min(20, 10 + 10 * (pcr_oi - 1) / 1.5)
        else:
            # Bearish signal (contrarian)
            pcr_oi_score = max(0, 10 - 10 * (1 - pcr_oi) / 0.5)
        
        sentiment_components.append({
            'component': 'PCR_OI',
            'raw_value': pcr_oi,
            'score': pcr_oi_score,
            'weight': 0.2,
            'contribution': pcr_oi_score * 0.2
        })
        
        # 2. PCR Volume component (0-15 points)
        pcr_volume = self.put_call_ratio_analysis.get('pcr_volume', 1.0)
        if pcr_volume > 1.0:
            # Bullish signal (contrarian)
            pcr_volume_score = min(15, 7.5 + 7.5 * (pcr_volume - 1) / 2)
        else:
            # Bearish signal (contrarian)
            pcr_volume_score = max(0, 7.5 - 7.5 * (1 - pcr_volume) / 0.6)
        
        sentiment_components.append({
            'component': 'PCR_Volume',
            'raw_value': pcr_volume,
            'score': pcr_volume_score,
            'weight': 0.15,
            'contribution': pcr_volume_score * 0.15
        })
        
        # 3. IV Skew component (0-15 points)
        skew_ratio = self.iv_skew_analysis.get('skew_ratio', 1.0)
        if skew_ratio > 1.0:
            # Bearish signal (direct)
            iv_skew_score = max(0, 7.5 - 7.5 * (skew_ratio - 1) / 0.3)
        else:
            # Bullish signal (direct)
            iv_skew_score = min(15, 7.5 + 7.5 * (1 - skew_ratio) / 0.3)
        
        sentiment_components.append({
            'component': 'IV_Skew',
            'raw_value': skew_ratio,
            'score': iv_skew_score,
            'weight': 0.15,
            'contribution': iv_skew_score * 0.15
        })
        
        # 4. Max Pain component (0-20 points)
        max_pain_dev = self.max_pain_point.get('deviation_pct', 0)
        max_pain_score = 10 + max_pain_dev * 2  # +2 points per 1% above spot, -2 points per 1% below
        max_pain_score = max(0, min(20, max_pain_score))
        
        sentiment_components.append({
            'component': 'Max_Pain',
            'raw_value': max_pain_dev,
            'score': max_pain_score,
            'weight': 0.2,
            'contribution': max_pain_score * 0.2
        })
        
        # 5. Gamma Exposure component (0-15 points)
        norm_gamma = self.dealer_gamma_exposure.get('normalized_net_gamma', 0)
        
        # Positive gamma is bearish from contrarian view (markets will be less volatile)
        # Negative gamma is bullish from contrarian view (markets will be more volatile)
        if norm_gamma > 0:
            gamma_score = max(0, 7.5 - 7.5 * norm_gamma / 0.3)
        else:
            gamma_score = min(15, 7.5 + 7.5 * abs(norm_gamma) / 0.3)
        
        sentiment_components.append({
            'component': 'Gamma_Exposure',
            'raw_value': norm_gamma,
            'score': gamma_score,
            'weight': 0.15,
            'contribution': gamma_score * 0.15
        })
        
        # 6. ATM IV Level component (0-15 points)
        atm_iv = self.iv_skew_analysis.get('atm_iv', 0.3)
        
        # Higher IV often correlates with fear/bearishness
        if atm_iv > 0.3:  # Higher than 30% IV
            iv_level_score = max(0, 7.5 - 7.5 * (atm_iv - 0.3) / 0.3)
        else:
            iv_level_score = min(15, 7.5 + 7.5 * (0.3 - atm_iv) / 0.2)
        
        sentiment_components.append({
            'component': 'ATM_IV_Level',
            'raw_value': atm_iv,
            'score': iv_level_score,
            'weight': 0.15,
            'contribution': iv_level_score * 0.15
        })
        
        # Calculate overall sentiment score (0-100)
        total_score = sum(component['contribution'] for component in sentiment_components) / sum(component['weight'] for component in sentiment_components) * 100
        
        # Interpret the score
        if total_score > 80:
            sentiment = "Strongly Bullish"
            interpretation = "Very optimistic market outlook, potentially overbought"
        elif total_score > 65:
            sentiment = "Bullish"
            interpretation = "Positive market outlook, upward bias expected"
        elif total_score > 55:
            sentiment = "Slightly Bullish"
            interpretation = "Mildly positive market outlook"
        elif total_score > 45:
            sentiment = "Neutral"
            interpretation = "Balanced market outlook, no clear bias"
        elif total_score > 35:
            sentiment = "Slightly Bearish"
            interpretation = "Mildly negative market outlook"
        elif total_score > 20:
            sentiment = "Bearish"
            interpretation = "Negative market outlook, downward bias expected"
        else:
            sentiment = "Strongly Bearish"
            interpretation = "Very pessimistic market outlook, potentially oversold"
        
        # Check for extreme readings (potential contrarian signals)
        contrarian_signal = None
        if total_score > 85:
            contrarian_signal = "Extreme bullishness - potential contrarian sell signal"
        elif total_score < 15:
            contrarian_signal = "Extreme bearishness - potential contrarian buy signal"
        
        self.market_sentiment_score = {
            'score': total_score,
            'sentiment': sentiment,
            'interpretation': interpretation,
            'contrarian_signal': contrarian_signal,
            'components': sentiment_components
        }
        
        return self.market_sentiment_score
    
    def extract_strike_specific_greeks(self) -> pd.DataFrame:
        """
        Extract strike-specific Greeks for advanced strategy building
        
        Returns:
        --------
        pd.DataFrame: DataFrame with strike-specific Greeks
        """
        # Select relevant columns
        if all(col in self.data.columns for col in ['strike', 'call_delta', 'put_delta', 'gamma', 'call_theta', 'put_theta', 'vega']):
            greeks_df = self.data[[
                'strike', 'moneyness', 'call_delta', 'put_delta', 'gamma', 
                'call_theta', 'put_theta', 'vega', 'call_oi', 'put_oi'
            ]].copy()
            
            # Calculate additional metrics
            greeks_df['delta_neutral_ratio'] = abs(greeks_df['put_delta'] / greeks_df['call_delta'].replace(0, 0.01))
            
            # Identify key strikes
            atm_idx = abs(greeks_df['moneyness'] - 1).idxmin()
            atm_strike = greeks_df.loc[atm_idx, 'strike']
            
            # Calculate deviation from ATM
            greeks_df['deviation_from_atm_pct'] = (greeks_df['strike'] - atm_strike) / atm_strike * 100
            
            # Identify high gamma strikes
            gamma_threshold = greeks_df['gamma'].max() * 0.7
            greeks_df['high_gamma'] = greeks_df['gamma'] > gamma_threshold
            
            # Calculate normalized values for comparison
            for col in ['gamma', 'call_theta', 'put_theta', 'vega']:
                if col in greeks_df.columns:
                    max_val = greeks_df[col].max()
                    if max_val > 0:
                        greeks_df[f'norm_{col}'] = greeks_df[col] / max_val
            
            # Sort by strike
            greeks_df = greeks_df.sort_values('strike')
            
            self.strike_specific_greeks = greeks_df
            return greeks_df
        else:
            return pd.DataFrame()
    
    def generate_grid_levels(self, num_levels: int = 5) -> List[Dict]:
        """
        Generate optimal grid trading levels based on option chain analysis
        
        Parameters:
        -----------
        num_levels : int
            Number of grid levels to generate
            
        Returns:
        --------
        List[Dict]: List of grid levels with metadata
        """
        # Make sure all analyses have been performed
        if not hasattr(self, 'support_resistance_levels') or not self.support_resistance_levels:
            self.analyze_support_resistance()
        
        if not hasattr(self, 'implied_range') or not self.implied_range:
            self.analyze_implied_range()
        
        if not hasattr(self, 'dealer_gamma_exposure') or not self.dealer_gamma_exposure:
            self.analyze_dealer_gamma()
        
        if not hasattr(self, 'market_sentiment_score') or not self.market_sentiment_score:
            self.calculate_market_sentiment()
        
        # Extract key price levels from analyses
        key_levels = []
        
        # 1. Add support/resistance levels
        for level in self.support_resistance_levels:
            key_levels.append({
                'price': level['strike'],
                'type': level['type'],
                'source': 'support_resistance',
                'strength': level['strength'],
                'deviation': level['deviation_from_spot_pct']
            })
        
        # 2. Add implied range boundaries
        if 'one_sigma_range' in self.implied_range:
            lower, upper = self.implied_range['one_sigma_range']
            
            key_levels.append({
                'price': lower,
                'type': 'support',
                'source': 'implied_range_lower',
                'strength': 0.7,
                'deviation': (lower / self.spot_price - 1) * 100
            })
            
            key_levels.append({
                'price': upper,
                'type': 'resistance',
                'source': 'implied_range_upper',
                'strength': 0.7,
                'deviation': (upper / self.spot_price - 1) * 100
            })
        
        # 3. Add gamma concentration zones
        if 'gamma_concentration' in self.dealer_gamma_exposure:
            for zone in self.dealer_gamma_exposure['gamma_concentration']:
                key_levels.append({
                    'price': zone['strike'],
                    'type': 'gamma_zone',
                    'source': 'dealer_gamma',
                    'strength': min(zone['concentration_pct'] / 100, 0.8),
                    'deviation': zone['deviation_from_spot_pct']
                })
        
        # Sort levels by price
        key_levels = sorted(key_levels, key=lambda x: x['price'])
        
        # Cluster nearby levels (within 0.5%)
        clustered_levels = []
        
        i = 0
        while i < len(key_levels):
            cluster = [key_levels[i]]
            j = i + 1
            
            # Find all levels within 0.5% of the current level
            while j < len(key_levels) and abs(key_levels[j]['price'] - key_levels[i]['price']) / key_levels[i]['price'] < 0.005:
                cluster.append(key_levels[j])
                j += 1
            
            # Combine cluster into a single level
            avg_price = sum(level['price'] for level in cluster) / len(cluster)
            max_strength = max(level['strength'] for level in cluster)
            sources = [level['source'] for level in cluster]
            types = [level['type'] for level in cluster]
            
            # Determine dominant type (excluding 'current')
            type_counts = {}
            for t in [t for t in types if t != 'current']:
                type_counts[t] = type_counts.get(t, 0) + 1
            
            if type_counts:
                dominant_type = max(type_counts.items(), key=lambda x: x[1])[0]
            else:
                dominant_type = 'neutral'
            
            # Calculate confirmation strength based on cluster size
            confirmation_strength = min(len(cluster) / 2, 1.0)
            combined_strength = max_strength * (0.8 + 0.2 * confirmation_strength)
            
            clustered_levels.append({
                'price': avg_price,
                'type': dominant_type,
                'sources': sources,
                'strength': combined_strength,
                'confirmation': confirmation_strength,
                'deviation': (avg_price / self.spot_price - 1) * 100
            })
            
            i = j
        
        # Select the best levels based on strength
        if len(clustered_levels) > num_levels:
            # Keep current price level if it exists
            current_level = next((level for level in clustered_levels if abs(level['deviation']) < 0.1), None)
            
            # Sort other levels by strength
            other_levels = [level for level in clustered_levels if abs(level['deviation']) >= 0.1]
            other_levels = sorted(other_levels, key=lambda x: x['strength'], reverse=True)
            
            # Select top N-1 levels if current level exists, or top N otherwise
            top_levels = other_levels[:num_levels - 1 if current_level else num_levels]
            
            if current_level:
                top_levels.append(current_level)
        else:
            top_levels = clustered_levels
        
        # If still not enough levels, add evenly spaced levels based on implied range
        if len(top_levels) < num_levels and 'lower_bound' in self.implied_range and 'upper_bound' in self.implied_range:
            lower_bound = self.implied_range['lower_bound']
            upper_bound = self.implied_range['upper_bound']
            
            missing_levels = num_levels - len(top_levels)
            existing_prices = [level['price'] for level in top_levels]
            
            # Fill in the gaps
            step = (upper_bound - lower_bound) / (missing_levels + 1)
            
            for i in range(1, missing_levels + 1):
                new_price = lower_bound + i * step
                
                # Skip if too close to existing level
                if all(abs(new_price - price) / price > 0.01 for price in existing_prices):
                    top_levels.append({
                        'price': new_price,
                        'type': 'grid_fill',
                        'sources': ['implied_range'],
                        'strength': 0.5,
                        'confirmation': 0.0,
                        'deviation': (new_price / self.spot_price - 1) * 100
                    })
        
        # Sort by price
        top_levels = sorted(top_levels, key=lambda x: x['price'])
        
        # Generate grid strategy details
        grid_levels = []
        
        # Get sentiment score (0-100)
        sentiment_score = self.market_sentiment_score['score']
        
        for i, level in enumerate(top_levels):
            # Determine if level is a buy or sell point
            if level['price'] < self.spot_price:
                action = 'BUY'
                
                # Adjust conviction based on bearish sentiment (contrarian)
                bearish_sentiment = max(0, 50 - sentiment_score) / 50
                conviction = level['strength'] * (1 + bearish_sentiment * 0.3)
                
            elif level['price'] > self.spot_price:
                action = 'SELL'
                
                # Adjust conviction based on bullish sentiment (contrarian)
                bullish_sentiment = max(0, sentiment_score - 50) / 50
                conviction = level['strength'] * (1 + bullish_sentiment * 0.3)
                
            else:
                # At current price
                action = 'NEUTRAL'
                conviction = 0.5
            
            # Calculate position size based on conviction and deviation
            allocation_pct = level['strength'] * 100 / sum(l['strength'] for l in top_levels)
            
            grid_levels.append({
                'level': i + 1,
                'price': level['price'],
                'price_formatted': f"{level['price']:.2f}",
                'deviation_pct': level['deviation'],
                'action': action,
                'type': level['type'],
                'sources': level['sources'],
                'strength': level['strength'],
                'conviction': min(conviction, 1.0),
                'allocation_pct': allocation_pct,
                'allocation_formatted': f"{allocation_pct:.1f}%"
            })
        
        self.grid_levels = grid_levels
        return grid_levels
    
    def get_full_analysis(self) -> Dict:
        """
        Get comprehensive option chain analysis with all insights
        
        Returns:
        --------
        Dict: Complete analysis with all insights
        """
        # Perform all analyses if not already done
        if not hasattr(self, 'max_pain_point') or not self.max_pain_point:
            self.analyze_max_pain()
        
        if not hasattr(self, 'iv_skew_analysis') or not self.iv_skew_analysis:
            self.analyze_iv_skew()
        
        if not hasattr(self, 'dealer_gamma_exposure') or not self.dealer_gamma_exposure:
            self.analyze_dealer_gamma()
        
        if not hasattr(self, 'support_resistance_levels') or not self.support_resistance_levels:
            self.analyze_support_resistance()
        
        if not hasattr(self, 'put_call_ratio_analysis') or not self.put_call_ratio_analysis:
            self.analyze_put_call_ratio()
        
        if not hasattr(self, 'implied_range') or not self.implied_range:
            self.analyze_implied_range()
        
        if not hasattr(self, 'market_sentiment_score') or not self.market_sentiment_score:
            self.calculate_market_sentiment()
        
        if not hasattr(self, 'strike_specific_greeks') or self.strike_specific_greeks is None or len(self.strike_specific_greeks) == 0:
            self.extract_strike_specific_greeks()
        
        if not hasattr(self, 'grid_levels') or not self.grid_levels:
            self.generate_grid_levels()
        
        # Compile all analyses into a comprehensive report
        return {
            'timestamp': datetime.now().isoformat(),
            'spot_price': self.spot_price,
            'expiry': self.data['expiry_date'].iloc[0] if 'expiry_date' in self.data.columns else None,
            'dte': self.data['dte'].iloc[0] if 'dte' in self.data.columns else 30,
            'max_pain': self.max_pain_point,
            'iv_skew': self.iv_skew_analysis,
            'dealer_gamma': self.dealer_gamma_exposure,
            'support_resistance': self.support_resistance_levels,
            'put_call_ratio': self.put_call_ratio_analysis,
            'implied_range': self.implied_range,
            'market_sentiment': self.market_sentiment_score,
            'grid_levels': self.grid_levels
        }

# Example usage function (continued)
def analyze_option_chain(option_data: pd.DataFrame, spot_price: float) -> Dict:
   """
   Analyze option chain data for grid trading
   
   Parameters:
   -----------
   option_data : pd.DataFrame
       DataFrame with option chain data
   spot_price : float
       Current spot price
       
   Returns:
   --------
   Dict: Analysis summary with grid levels and key insights
   """
   analyzer = OptionChainAnalyzer(option_data, spot_price)
   
   # Get comprehensive analysis
   analysis = analyzer.get_full_analysis()
   
   # Create a concise summary of key insights
   key_insights = {
       "max_pain": {
           "level": analysis['max_pain']['price'],
           "impact": analysis['max_pain']['impact'],
           "explanation": "Maximum pain point represents the strike price where option sellers have minimal losses. Markets often gravitate toward this price at expiration."
       },
       "iv_skew": {
           "skew_ratio": analysis['iv_skew']['skew_ratio'],
           "interpretation": analysis['iv_skew']['interpretation'],
           "explanation": "IV skew measures the premium difference between puts and calls. High put premium indicates downside fear; high call premium indicates upside optimism."
       },
       "dealer_gamma": {
           "impact": analysis['dealer_gamma']['gamma_impact'],
           "behavior": analysis['dealer_gamma']['hedging_behavior'],
           "explanation": "Dealer gamma exposure drives market stability. Positive gamma creates stability; negative gamma amplifies volatility as dealers need to buy high and sell low."
       },
       "support_resistance": {
           "levels": [{"price": level['strike'], "type": level['type'], "strength": f"{level['strength']*100:.0f}%"} 
                     for level in analysis['support_resistance'][:3]],
           "explanation": "Key price levels where buying/selling interest is concentrated, validated through option positioning."
       },
       "put_call_ratio": {
           "pcr_oi": analysis['put_call_ratio']['pcr_oi'],
           "sentiment": analysis['put_call_ratio']['oi_sentiment'],
           "contrarian": analysis['put_call_ratio']['oi_contrarian'],
           "explanation": "Put-Call Ratio measures overall market sentiment. High PCR often signals bearish sentiment but can be a bullish contrarian indicator."
       },
       "implied_range": {
           "range": f"{analysis['implied_range']['lower_bound']:.2f} - {analysis['implied_range']['upper_bound']:.2f}",
           "probability": f"{analysis['implied_range']['one_sigma_probability']:.1f}%",
           "explanation": "Price range expected by the options market, with the given probability. Derived from implied volatility."
       },
       "market_sentiment": {
           "score": f"{analysis['market_sentiment']['score']:.1f}/100",
           "sentiment": analysis['market_sentiment']['sentiment'],
           "explanation": "Composite sentiment score derived from multiple option indicators, quantifying market psychology."
       }
   }
   
   # Format grid levels for easy implementation
   formatted_grid = []
   for level in analysis['grid_levels']:
       formatted_grid.append({
           "level": level['level'],
           "price": level['price_formatted'],
           "action": level['action'],
           "deviation": f"{level['deviation_pct']:.2f}%",
           "conviction": f"{level['conviction']*100:.0f}%",
           "allocation": level['allocation_formatted'],
           "source": ", ".join([s.replace('_', ' ').title() for s in level['sources'][:2]])
       })
   
   # Create final result
   result = {
       "spot_price": spot_price,
       "expiry_days": analysis['dte'],
       "key_insights": key_insights,
       "grid_levels": formatted_grid,
       "market_sentiment": {
           "score": analysis['market_sentiment']['score'],
           "sentiment": analysis['market_sentiment']['sentiment'],
           "interpretation": analysis['market_sentiment']['interpretation'],
           "contrarian_signal": analysis['market_sentiment']['contrarian_signal']
       }
   }
   
   return result


# Example demo
if __name__ == "__main__":
   # Create sample data
   import numpy as np
   
   # Generate mock option chain for testing
   spot_price = 22000  # Example: NIFTY at 22000
   
   # Create strikes around the spot price
   strikes = np.linspace(spot_price * 0.9, spot_price * 1.1, 21)
   
   # Generate sample option prices
   time_to_expiry = 30/365  # 30 days
   risk_free_rate = 0.05
   implied_vol = 0.18  # 18% IV
   
   import scipy.stats as stats
   
   def bs_call(S, K, T, r, sigma):
       d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
       d2 = d1 - sigma * np.sqrt(T)
       return S * stats.norm.cdf(d1) - K * np.exp(-r*T) * stats.norm.cdf(d2)
   
   def bs_put(S, K, T, r, sigma):
       d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
       d2 = d1 - sigma * np.sqrt(T)
       return K * np.exp(-r*T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)
   
   # Create sample data
   data = []
   for strike in strikes:
       # Base IV with a smile
       strike_iv = implied_vol * (1 + 0.5 * ((strike/spot_price - 1) ** 2))
       
       # Calculate prices
       call_price = bs_call(spot_price, strike, time_to_expiry, risk_free_rate, strike_iv)
       put_price = bs_put(spot_price, strike, time_to_expiry, risk_free_rate, strike_iv)
       
       # Generate OI with max at spot price, dropping at wings
       moneyness = strike/spot_price
       base_oi = 1000 * np.exp(-20 * (moneyness - 1) ** 2)
       
       # More call OI above spot, more put OI below spot
       call_oi = base_oi * (1 + max(0, (moneyness - 1) * 3))
       put_oi = base_oi * (1 + max(0, (1 - moneyness) * 3))
       
       # Volume is 10% of OI with some random noise
       call_volume = call_oi * 0.1 * (0.8 + 0.4 * np.random.random())
       put_volume = put_oi * 0.1 * (0.8 + 0.4 * np.random.random())
       
       data.append({
           'strike': strike,
           'call_price': call_price,
           'put_price': put_price,
           'call_iv': strike_iv,
           'put_iv': strike_iv,
           'call_oi': call_oi,
           'put_oi': put_oi,
           'call_volume': call_volume,
           'put_volume': put_volume,
           'expiry_date': '2025-05-30'
       })
   
   # Create DataFrame
   option_chain = pd.DataFrame(data)
   
   # Run analysis
   result = analyze_option_chain(option_chain, spot_price)
   
   # Print key insights
   print("\n==== OPTION CHAIN ANALYSIS ====")
   print(f"NIFTY Spot: {spot_price} | Expiry: {result['expiry_days']} days\n")
   
   print("📍 MAX PAIN:", result['key_insights']['max_pain']['level'])
   print("   " + result['key_insights']['max_pain']['impact'])
   
   print("\n🔥 IV SKEW:", result['key_insights']['iv_skew']['skew_ratio'])
   print("   " + result['key_insights']['iv_skew']['interpretation'])
   
   print("\n🧠 DEALER GAMMA:", result['key_insights']['dealer_gamma']['impact'])
   print("   " + result['key_insights']['dealer_gamma']['behavior'])
   
   print("\n📈 SUPPORT/RESISTANCE LEVELS:")
   for level in result['key_insights']['support_resistance']['levels']:
       print(f"   {level['price']:.2f} ({level['type']}, {level['strength']} strength)")
   
   print("\n📊 PUT-CALL RATIO:", result['key_insights']['put_call_ratio']['pcr_oi'])
   print("   Sentiment:", result['key_insights']['put_call_ratio']['sentiment'])
   print("   Contrarian:", result['key_insights']['put_call_ratio']['contrarian'])
   
   print("\n🧮 IMPLIED RANGE:", result['key_insights']['implied_range']['range'])
   print(f"   {result['key_insights']['implied_range']['probability']} probability")
   
   print("\n🤖 MARKET SENTIMENT:", result['key_insights']['market_sentiment']['score'])
   print("   " + result['key_insights']['market_sentiment']['sentiment'])
   
   # Print grid levels
   print("\n🔗 GRID TRADING LEVELS:")
   print("   Level    Price     Action    Deviation    Conviction    Allocation")
   print("   -----    -----     ------    ---------    ----------    ----------")
   for level in result['grid_levels']:
       print(f"   {level['level']}        {level['price']}    {level['action']}     {level['deviation']}      {level['conviction']}        {level['allocation']}")
   
   print("\nAnalysis Complete!")