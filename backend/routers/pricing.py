import numpy as np
from fastapi import APIRouter, HTTPException
from backend.schemas import OptionRequest, PricingResponse

router = APIRouter(prefix="/api/price", tags=["Pricing"])


@router.post("/", response_model=PricingResponse)
async def price_option(req: OptionRequest):
    """
    Price a European option using all methods:
    Black-Scholes, Naive MC, Antithetic, Control Variates, Importance Sampling.
    """
    try:
        from mc_pricer.black_scholes import black_scholes_price
        from mc_pricer.simulation import monte_carlo_price
        from mc_pricer.variance_reduction import (
            antithetic_price,
            control_variate_price,
            importance_sampling_price
        )

        np.random.seed(42)

        bs    = black_scholes_price(req.S, req.K, req.T, req.r, req.sigma, req.option_type)
        mc    = monte_carlo_price(req.S, req.K, req.T, req.r, req.sigma, req.N, req.option_type)
        anti  = antithetic_price(req.S, req.K, req.T, req.r, req.sigma, req.N, req.option_type)
        cv    = control_variate_price(req.S, req.K, req.T, req.r, req.sigma, req.N, req.option_type)
        imp   = importance_sampling_price(req.S, req.K, req.T, req.r, req.sigma, req.N, req.option_type)

        return PricingResponse(
            bs_price            = round(bs,   4),
            mc_price            = round(mc,   4),
            antithetic          = round(anti, 4),
            control_variate     = round(cv,   4),
            importance_sampling = round(imp,  4),
            error_pct           = round(abs(mc - bs) / bs * 100, 4),
            option_type         = req.option_type,
            parameters          = {
                "S": req.S, "K": req.K, "T": req.T,
                "r": req.r, "sigma": req.sigma, "N": req.N
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok", "engine": "mc_pricer v0.1.0"}