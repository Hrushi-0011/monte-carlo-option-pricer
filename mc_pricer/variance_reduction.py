import numpy as np
from mc_pricer.black_scholes import black_scholes_price


# ════════════════════════════════════════════════════════════════
# 1. ANTITHETIC VARIATES
# ════════════════════════════════════════════════════════════════

def antithetic_price(S, K, T, r, sigma, n_simulations=100000, option_type='call'):
    """
    Price a European option using Antithetic Variates variance reduction.

    THEORY:
    Instead of generating N random numbers Z, we generate N/2 and pair
    each Z with its mirror -Z. Since Z and -Z are negatively correlated,
    their payoffs cancel out much of the noise, giving a more stable average
    with the same number of simulations.

    Variance reduction formula:
        Var(antithetic) = (Var(Z) + Var(-Z) + 2*Cov(Z,-Z)) / 4
        Since Cov is negative, total variance is significantly reduced.

    Parameters:
        S            : Current stock price
        K            : Strike price
        T            : Time to expiry in years
        r            : Risk-free rate
        sigma        : Volatility
        n_simulations: Total paths (half used for Z, half for -Z)
        option_type  : 'call' or 'put'

    Returns:
        Estimated option price (float)
    """
    half = n_simulations // 2

    # Generate only half the random numbers
    Z = np.random.standard_normal(half)

    # GBM formula for Z and -Z
    drift = (r - 0.5 * sigma**2) * T
    diffusion = sigma * np.sqrt(T)

    S_T_positive = S * np.exp(drift + diffusion * Z)   # normal paths
    S_T_negative = S * np.exp(drift + diffusion * (-Z)) # mirror paths

    # Payoffs for both sets
    if option_type == 'call':
        payoffs_pos = np.maximum(S_T_positive - K, 0)
        payoffs_neg = np.maximum(S_T_negative - K, 0)
    elif option_type == 'put':
        payoffs_pos = np.maximum(K - S_T_positive, 0)
        payoffs_neg = np.maximum(K - S_T_negative, 0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    # Average the paired payoffs — this is the key step
    # Each pair (Z, -Z) gives one averaged payoff
    antithetic_payoffs = (payoffs_pos + payoffs_neg) / 2

    price = np.exp(-r * T) * np.mean(antithetic_payoffs)
    return price


# ════════════════════════════════════════════════════════════════
# 2. CONTROL VARIATES
# ════════════════════════════════════════════════════════════════

def control_variate_price(S, K, T, r, sigma, n_simulations=100000, option_type='call'):
    """
    Price a European option using Control Variates variance reduction.

    THEORY:
    We use Black-Scholes as a "control" — a variable whose true value
    we know exactly. We measure how much our simulation deviates from
    the control's known truth, then apply that correction to our estimate.

    Estimator:
        MC_cv = MC_naive + beta * (BS_exact - MC_of_BS)

    Where beta is the optimal coefficient that minimizes variance:
        beta = -Cov(payoff, control) / Var(control)

    Since Black-Scholes is highly correlated with our Monte Carlo payoffs,
    the correction dramatically reduces variance.

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
    # Step 1: Simulate final stock prices
    Z = np.random.standard_normal(n_simulations)
    drift = (r - 0.5 * sigma**2) * T
    S_T = S * np.exp(drift + sigma * np.sqrt(T) * Z)

    # Step 2: Compute target payoffs (what we want to price)
    if option_type == 'call':
        payoffs = np.maximum(S_T - K, 0)
    elif option_type == 'put':
        payoffs = np.maximum(K - S_T, 0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    # Step 3: Compute control payoffs using same simulated paths
    # We use the underlying stock price S_T as a control variable
    # because we know its exact expected value: S * exp(r*T)
    control_payoffs = S_T
    control_expected = S * np.exp(r * T)  # Known exact value

    # Step 4: Compute optimal beta via covariance
    # beta minimizes variance of the corrected estimator
    covariance_matrix = np.cov(payoffs, control_payoffs)
    beta = -covariance_matrix[0, 1] / covariance_matrix[1, 1]

    # Step 5: Apply correction
    corrected_payoffs = payoffs + beta * (control_expected - control_payoffs)

    price = np.exp(-r * T) * np.mean(corrected_payoffs)
    return price


# ════════════════════════════════════════════════════════════════
# 3. IMPORTANCE SAMPLING
# ════════════════════════════════════════════════════════════════

def importance_sampling_price(S, K, T, r, sigma, n_simulations=100000, option_type='call'):
    """
    Price a European option using Importance Sampling variance reduction.

    THEORY:
    Naive Monte Carlo wastes simulations on paths where the option expires
    worthless (zero payoff). Importance Sampling shifts the distribution
    to sample more from the region where payoffs are non-zero (in-the-money).

    We shift the mean of Z by a constant mu_shift toward in-the-money region,
    then correct for this shift using a likelihood ratio weight:
        weight = exp(-mu_shift * Z - 0.5 * mu_shift^2)

    This is particularly powerful for deep out-of-the-money options where
    naive Monte Carlo rarely generates profitable paths.

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
    # Compute the shift that centers sampling near the strike price
    # This is the log-moneyness adjusted for drift
    log_moneyness = np.log(K / S)
    drift = (r - 0.5 * sigma**2) * T

    # mu_shift moves the distribution center toward the strike
    mu_shift = (log_moneyness - drift) / (sigma * np.sqrt(T))

    # Clamp shift to avoid extreme sampling distortion
    mu_shift = np.clip(mu_shift, -3, 3)

    # Sample from shifted distribution
    Z = np.random.standard_normal(n_simulations) + mu_shift

    # Simulate stock prices under shifted measure
    S_T = S * np.exp(drift + sigma * np.sqrt(T) * Z)

    # Compute payoffs
    if option_type == 'call':
        payoffs = np.maximum(S_T - K, 0)
    elif option_type == 'put':
        payoffs = np.maximum(K - S_T, 0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    # Likelihood ratio correction — unbiases the shifted sampling
    likelihood_ratio = np.exp(-mu_shift * Z + 0.5 * mu_shift**2)
    weighted_payoffs = payoffs * likelihood_ratio

    price = np.exp(-r * T) * np.mean(weighted_payoffs)
    return price


# ════════════════════════════════════════════════════════════════
# 4. COMPARISON FUNCTION
# ════════════════════════════════════════════════════════════════

def compare_all_methods(S, K, T, r, sigma, n_simulations=100000, option_type='call'):
    """
    Run all pricing methods and return a comparison dictionary.

    Returns:
        dict with keys: bs, naive, antithetic, control_variate, importance_sampling
        Each value is a dict with 'price' and 'error_pct'
    """
    from mc_pricer.simulation import monte_carlo_price

    np.random.seed(42)

    bs = black_scholes_price(S, K, T, r, sigma, option_type)

    methods = {
        'Black-Scholes (Exact)' : bs,
        'Naive Monte Carlo'     : monte_carlo_price(S, K, T, r, sigma, n_simulations, option_type),
        'Antithetic Variates'   : antithetic_price(S, K, T, r, sigma, n_simulations, option_type),
        'Control Variates'      : control_variate_price(S, K, T, r, sigma, n_simulations, option_type),
        'Importance Sampling'   : importance_sampling_price(S, K, T, r, sigma, n_simulations, option_type),
    }

    results = {}
    for name, price in methods.items():
        error = abs(price - bs)
        error_pct = (error / bs) * 100
        results[name] = {
            'price'     : price,
            'error'     : error,
            'error_pct' : error_pct
        }

    return results