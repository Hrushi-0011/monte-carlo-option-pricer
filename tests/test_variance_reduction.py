import pytest
import numpy as np
from mc_pricer.black_scholes import black_scholes_price
from mc_pricer.variance_reduction import (
    antithetic_price,
    control_variate_price,
    importance_sampling_price
)

S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
BS_CALL = black_scholes_price(S, K, T, r, sigma, 'call')
BS_PUT  = black_scholes_price(S, K, T, r, sigma, 'put')

class TestVarianceReduction:

    def test_antithetic_call_accuracy(self):
        """Antithetic call price within 1% of Black-Scholes."""
        np.random.seed(42)
        price = antithetic_price(S, K, T, r, sigma, 100000, 'call')
        assert abs(price - BS_CALL) / BS_CALL < 0.01

    def test_antithetic_put_accuracy(self):
        np.random.seed(42)
        price = antithetic_price(S, K, T, r, sigma, 100000, 'put')
        assert abs(price - BS_PUT) / BS_PUT < 0.01

    def test_control_variate_call_accuracy(self):
        """Control variate should be tighter than 0.5% error."""
        np.random.seed(42)
        price = control_variate_price(S, K, T, r, sigma, 100000, 'call')
        assert abs(price - BS_CALL) / BS_CALL < 0.005

    def test_control_variate_put_accuracy(self):
        np.random.seed(42)
        price = control_variate_price(S, K, T, r, sigma, 100000, 'put')
        assert abs(price - BS_PUT) / BS_PUT < 0.005

    def test_importance_sampling_call_accuracy(self):
        np.random.seed(42)
        price = importance_sampling_price(S, K, T, r, sigma, 100000, 'call')
        assert abs(price - BS_CALL) / BS_CALL < 0.01

    def test_all_prices_positive(self):
        np.random.seed(42)
        for fn in [antithetic_price, control_variate_price, importance_sampling_price]:
            price = fn(S, K, T, r, sigma, 10000, 'call')
            assert price > 0

    def test_invalid_option_type(self):
        with pytest.raises(ValueError):
            antithetic_price(S, K, T, r, sigma, 1000, 'invalid')