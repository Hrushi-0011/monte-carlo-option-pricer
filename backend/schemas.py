from pydantic import BaseModel, Field
from typing import Literal


# ── Request Models ────────────────────────────────────────────────────────────

class OptionRequest(BaseModel):
    S     : float = Field(100.0,  gt=0,         description="Current stock price")
    K     : float = Field(100.0,  gt=0,         description="Strike price")
    T     : float = Field(1.0,    gt=0, le=10,  description="Time to expiry in years")
    r     : float = Field(0.05,   ge=0, le=1,   description="Risk-free rate")
    sigma : float = Field(0.20,   gt=0, le=5,   description="Volatility")
    N     : int   = Field(100000, gt=0, le=500000, description="Number of simulations")
    option_type: Literal['call', 'put'] = 'call'

    model_config = {
        "json_schema_extra": {
            "example": {
                "S": 100, "K": 100, "T": 1.0,
                "r": 0.05, "sigma": 0.20,
                "N": 100000, "option_type": "call"
            }
        }
    }


class ConvergenceRequest(BaseModel):
    S          : float = Field(100.0, gt=0)
    K          : float = Field(100.0, gt=0)
    T          : float = Field(1.0,   gt=0)
    r          : float = Field(0.05,  ge=0)
    sigma      : float = Field(0.20,  gt=0)
    option_type: Literal['call', 'put'] = 'call'
    n_points   : int   = Field(20, ge=5, le=40)


# ── Response Models ───────────────────────────────────────────────────────────

class PricingResponse(BaseModel):
    bs_price      : float
    mc_price      : float
    antithetic    : float
    control_variate: float
    importance_sampling: float
    error_pct     : float
    option_type   : str
    parameters    : dict


class GreeksResponse(BaseModel):
    mc_greeks : dict
    bs_greeks : dict
    parameters: dict


class ConvergenceResponse(BaseModel):
    sim_counts    : list[int]
    errors_naive  : list[float]
    errors_anti   : list[float]
    errors_cv     : list[float]
    bs_price      : float


class SimulationResponse(BaseModel):
    time_axis  : list[float]
    paths      : list[list[float]]
    mean_path  : list[float]
    final_prices: list[float]


class AIExplanationResponse(BaseModel):
    explanation: str