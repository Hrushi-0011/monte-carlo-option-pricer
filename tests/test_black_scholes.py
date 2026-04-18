import numpy as np
from scipy.stats import norm

def black_scholes_price(S, K, T, r, sigma, option_type='call'):
    """
    Calculate the exact Black-Scholes price for a European option.

    Parameters:
        S     : Current stock price
        K     : Strike price
        T     : Time to expiry in years
        r     : Risk-free interest rate
        sigma : Volatility
        option_type : 'call' or 'put'

    Returns:
        Option price (float)
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return price

import pytest

from mc_pricer.black_scholes import black_scholes_price

class TestBlackScholes:

    def test_call_price_positive(self):
        """Option prices must always be positive."""
        price = black_scholes_price(100, 100, 1.0, 0.05, 0.20, 'call')
        assert price > 0

    def test_put_price_positive(self):
        price = black_scholes_price(100, 100, 1.0, 0.05, 0.20, 'put')
        assert price > 0

    def test_put_call_parity(self):
        """
        Put-Call Parity: fundamental law of options pricing.
        Call - Put = S - K * exp(-rT)
        If this doesn't hold, something is mathematically broken.
        """
        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        call = black_scholes_price(S, K, T, r, sigma, 'call')
        put  = black_scholes_price(S, K, T, r, sigma, 'put')
        parity_lhs = call - put
        parity_rhs = S - K * np.exp(-r * T)
        assert abs(parity_lhs - parity_rhs) < 1e-10

    def test_known_value(self):
        """Test against a known Black-Scholes value."""
        price = black_scholes_price(100, 100, 1.0, 0.05, 0.20, 'call')
        assert abs(price - 10.4506) < 0.01

    def test_invalid_option_type(self):
        """Should raise an error for invalid option type."""
        with pytest.raises(ValueError):
            black_scholes_price(100, 100, 1.0, 0.05, 0.20, 'invalid')