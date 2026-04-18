import numpy as np

def simulate_gbm(S, T, r, sigma, n_simulations, n_steps=1):
    """
    Simulate future stock prices using Geometric Brownian Motion.

    Parameters:
        S            : Current stock price
        T            : Time to expiry in years
        r            : Risk-free rate
        sigma        : Volatility
        n_simulations: Number of simulated paths
        n_steps      : Number of time steps

    Returns:
        Array of simulated final stock prices
    """
    dt = T / n_steps
    Z = np.random.standard_normal((n_simulations, n_steps))
    log_returns = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    S_T = S * np.exp(np.sum(log_returns, axis=1))
    return S_T


def monte_carlo_price(S, K, T, r, sigma, n_simulations=100000, option_type='call'):
    """
    Price a European option using Monte Carlo simulation.

    Parameters:
        S            : Current stock price
        K            : Strike price
        T            : Time to expiry in years
        r            : Risk-free rate
        sigma        : Volatility
        n_simulations: Number of simulated paths
        option_type  : 'call' or 'put'

    Returns:
        Estimated option price (float)
    """
    S_T = simulate_gbm(S, T, r, sigma, n_simulations)

    if option_type == 'call':
        payoffs = np.maximum(S_T - K, 0)
    elif option_type == 'put':
        payoffs = np.maximum(K - S_T, 0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    price = np.exp(-r * T) * np.mean(payoffs)
    return price