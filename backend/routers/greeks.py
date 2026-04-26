import numpy as np
from fastapi import APIRouter, HTTPException
from backend.schemas import OptionRequest, GreeksResponse

router = APIRouter(prefix="/api/greeks", tags=["Greeks"])


@router.post("/", response_model=GreeksResponse)
async def compute_greeks(req: OptionRequest):
    """
    Compute all Greeks via Monte Carlo finite differences
    and compare with Black-Scholes analytical values.
    """
    try:
        from mc_pricer.greeks import all_greeks

        np.random.seed(42)

        mc_g, bs_g = all_greeks(
            req.S, req.K, req.T, req.r, req.sigma,
            n_simulations=50000,
            option_type=req.option_type
        )

        # Round all values for clean JSON response
        mc_rounded = {k: round(float(v), 6) for k, v in mc_g.items()}
        bs_rounded = {k: round(float(v), 6) for k, v in bs_g.items()}

        return GreeksResponse(
            mc_greeks  = mc_rounded,
            bs_greeks  = bs_rounded,
            parameters = {
                "S": req.S, "K": req.K, "T": req.T,
                "r": req.r, "sigma": req.sigma
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))