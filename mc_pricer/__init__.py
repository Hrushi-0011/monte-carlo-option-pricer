"""
mc_pricer — Monte Carlo Option Pricing Engine
=============================================
A production-grade Monte Carlo simulation engine for pricing
European options with variance reduction techniques.

Usage:
    from mc_pricer.black_scholes import black_scholes_price
    from mc_pricer.simulation import monte_carlo_price
    from mc_pricer.variance_reduction import antithetic_price
    from mc_pricer.greeks import all_greeks

Version: 0.1.0
"""

from mc_pricer.black_scholes import black_scholes_price
from mc_pricer.simulation import simulate_gbm, monte_carlo_price

__version__ = "0.1.0"
__author__  = "Your Name"
__all__ = [
    "black_scholes_price",
    "simulate_gbm",
    "monte_carlo_price",
]