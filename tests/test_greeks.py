import pytest
import numpy as np
from mc_pricer.greeks import delta, gamma, vega, all_greeks
from mc_pricer.black_scholes import black_scholes_price

S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20

class TestGreeks:

    def test_call_delta_range(self):
        """Call delta must be between 0 and 1."""
        np.random.seed(42)
        d = delta(S, K, T, r, sigma, 50000, 'call')
        assert 0 < d < 1

    def test_put_delta_range(self):
        """Put delta must be between -1 and 0."""
        np.random.seed(42)
        d = delta(S, K, T, r, sigma, 50000, 'put')
        assert -1 < d < 0

    def test_gamma_positive(self):
        """Gamma must always be positive for long options."""
        np.random.seed(42)
        g = gamma(S, K, T, r, sigma, 50000, 'call')
        assert g > 0

    def test_vega_positive(self):
        """Vega must always be positive — more vol = more expensive option."""
        np.random.seed(42)
        v = vega(S, K, T, r, sigma, 50000, 'call')
        assert v > 0

    def test_delta_accuracy_vs_bs(self):
        """MC delta within 5% of BS analytical delta."""
        np.random.seed(42)
        from scipy.stats import norm
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * np.sqrt(T))
        bs_delta = norm.cdf(d1)
        mc_delta = delta(S, K, T, r, sigma, 50000, 'call')
        assert abs(mc_delta - bs_delta) / bs_delta < 0.05

    def test_all_greeks_returns_correct_keys(self):
        np.random.seed(42)
        mc_g, bs_g = all_greeks(S, K, T, r, sigma, 10000)
        expected = {'Delta', 'Gamma', 'Vega', 'Theta', 'Rho'}
        assert set(mc_g.keys()) == expected
        assert set(bs_g.keys()) == expected