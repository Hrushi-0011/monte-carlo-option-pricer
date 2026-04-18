import numpy as np
from mc_pricer.black_scholes import black_scholes_price


def _mc_price_seeded(S, K, T, r, sigma, n_simulations, option_type, seed):
    """Price with a fixed seed so bumped calculations use same random paths."""
    np.random.seed(seed)
    from mc_pricer.simulation import monte_carlo_price
    return monte_carlo_price(S, K, T, r, sigma, n_simulations, option_type)


def delta(S, K, T, r, sigma, n_simulations=50000, option_type='call', h=1.0):
    """
    Estimate Delta — dV/dS
    How much does the option price change for a $1 move in stock price?
    Call delta: 0 to 1. Put delta: -1 to 0.
    h=1.0 means we bump stock price by $1 (1% on a $100 stock).
    """
    seed = 42
    price_up   = _mc_price_seeded(S + h, K, T, r, sigma, n_simulations, option_type, seed)
    price_down = _mc_price_seeded(S - h, K, T, r, sigma, n_simulations, option_type, seed)
    return (price_up - price_down) / (2 * h)


def gamma(S, K, T, r, sigma, n_simulations=50000, option_type='call', h=1.0):
    """
    Estimate Gamma — d²V/dS²
    How much does Delta change for a $1 move in stock price?
    Always positive for long options.
    """
    seed = 42
    price_up   = _mc_price_seeded(S + h, K, T, r, sigma, n_simulations, option_type, seed)
    price_mid  = _mc_price_seeded(S,     K, T, r, sigma, n_simulations, option_type, seed)
    price_down = _mc_price_seeded(S - h, K, T, r, sigma, n_simulations, option_type, seed)
    return (price_up - 2 * price_mid + price_down) / (h ** 2)


def vega(S, K, T, r, sigma, n_simulations=50000, option_type='call', h=0.01):
    """
    Estimate Vega — dV/dσ
    How much does the option price change for a 1% vol move?
    Always positive — more volatility = more expensive option.
    h=0.01 means 1% volatility bump.
    """
    seed = 42
    price_up   = _mc_price_seeded(S, K, T, r, sigma + h, n_simulations, option_type, seed)
    price_down = _mc_price_seeded(S, K, T, r, sigma - h, n_simulations, option_type, seed)
    return (price_up - price_down) / (2 * h)


def theta(S, K, T, r, sigma, n_simulations=50000, option_type='call', h=1/365):
    """
    Estimate Theta — daily value decay.
    Returns price change for one day passing (negative for long options).
    """
    seed = 42
    price_now  = _mc_price_seeded(S, K, T,     r, sigma, n_simulations, option_type, seed)
    price_next = _mc_price_seeded(S, K, T - h, r, sigma, n_simulations, option_type, seed)
    # Don't divide by h — we want the raw daily change, not annualized rate
    return price_next - price_now


def rho(S, K, T, r, sigma, n_simulations=50000, option_type='call', h=0.01):
    """
    Estimate Rho — sensitivity to 1% interest rate move.
    """
    seed = 42
    price_up   = _mc_price_seeded(S, K, T, r + h, sigma, n_simulations, option_type, seed)
    price_down = _mc_price_seeded(S, K, T, r - h, sigma, n_simulations, option_type, seed)
    # Divide by 200 instead of 2*h to express per 1% (0.01) move
    return (price_up - price_down) / (2 * h) / 100


def all_greeks(S, K, T, r, sigma, n_simulations=50000, option_type='call'):
    """
    Compute all Greeks and compare with Black-Scholes analytical values.

    Returns:
        mc_greeks : dict of Monte Carlo estimated Greeks
        bs_greeks : dict of Black-Scholes exact Greeks
    """
    from scipy.stats import norm

    mc_greeks = {
        'Delta' : delta(S, K, T, r, sigma, n_simulations, option_type),
        'Gamma' : gamma(S, K, T, r, sigma, n_simulations, option_type),
        'Vega'  : vega(S, K, T, r, sigma, n_simulations, option_type),
        'Theta' : theta(S, K, T, r, sigma, n_simulations, option_type),
        'Rho'   : rho(S, K, T, r, sigma, n_simulations, option_type),
    }

    # Black-Scholes analytical Greeks
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        bs_delta = norm.cdf(d1)
        bs_rho   = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        bs_delta = norm.cdf(d1) - 1
        bs_rho   = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

    bs_gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    bs_vega  = S * norm.pdf(d1) * np.sqrt(T)
    bs_theta = (
        -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        - r * K * np.exp(-r * T) * norm.cdf(d2 if option_type == 'call' else -d2)
    ) / 365

    bs_greeks = {
        'Delta' : bs_delta,
        'Gamma' : bs_gamma,
        'Vega'  : bs_vega,
        'Theta' : bs_theta,
        'Rho'   : bs_rho,
    }

    return mc_greeks, bs_greeks