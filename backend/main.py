import sys
import os

# Make mc_pricer importable from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from backend.routers import pricing, greeks, analysis
from backend.schemas import OptionRequest, AIExplanationResponse
from backend.ai_explainer import explain_results

load_dotenv()

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Monte Carlo Option Pricer API",
    description = "Production-grade option pricing engine with variance reduction",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc"
)

# ── CORS — allow React frontend to talk to this API ───────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(pricing.router)
app.include_router(greeks.router)
app.include_router(analysis.router)


# ── AI Explanation Endpoint ───────────────────────────────────────────────────
@app.post("/api/explain", response_model=AIExplanationResponse, tags=["AI"])
async def get_explanation(req: OptionRequest):
    """
    Run full pricing + Greeks, then ask Claude to explain results
    in plain English.
    """
    try:
        import numpy as np
        from mc_pricer.black_scholes import black_scholes_price
        from mc_pricer.simulation import monte_carlo_price
        from mc_pricer.variance_reduction import antithetic_price, control_variate_price, importance_sampling_price
        from mc_pricer.greeks import all_greeks

        np.random.seed(42)

        bs   = black_scholes_price(req.S, req.K, req.T, req.r, req.sigma, req.option_type)
        mc   = monte_carlo_price(req.S, req.K, req.T, req.r, req.sigma, req.N, req.option_type)
        anti = antithetic_price(req.S, req.K, req.T, req.r, req.sigma, req.N, req.option_type)
        cv   = control_variate_price(req.S, req.K, req.T, req.r, req.sigma, req.N, req.option_type)
        imp  = importance_sampling_price(req.S, req.K, req.T, req.r, req.sigma, req.N, req.option_type)
        mc_g, bs_g = all_greeks(req.S, req.K, req.T, req.r, req.sigma, 50000, req.option_type)

        pricing_data = {
            "bs_price"           : round(bs,   4),
            "mc_price"           : round(mc,   4),
            "antithetic"         : round(anti, 4),
            "control_variate"    : round(cv,   4),
            "importance_sampling": round(imp,  4),
            "error_pct"          : round(abs(mc - bs) / bs * 100, 4),
            "parameters"         : {
                "S": req.S, "K": req.K, "T": req.T,
                "r": req.r, "sigma": req.sigma, "N": req.N
            }
        }

        greeks_data = {
            "mc_greeks": {k: round(float(v), 6) for k, v in mc_g.items()},
            "bs_greeks": {k: round(float(v), 6) for k, v in bs_g.items()}
        }

        explanation = explain_results(pricing_data, greeks_data, req.option_type)
        return AIExplanationResponse(explanation=explanation)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message"  : "Monte Carlo Option Pricer API",
        "version"  : "1.0.0",
        "docs"     : "/docs",
        "endpoints": ["/api/price", "/api/greeks", "/api/analysis/convergence", "/api/analysis/simulate", "/api/explain"]
    }