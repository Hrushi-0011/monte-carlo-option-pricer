import numpy as np
from fastapi import APIRouter, HTTPException
from backend.schemas import ConvergenceRequest, ConvergenceResponse, SimulationResponse, OptionRequest

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post("/convergence", response_model=ConvergenceResponse)
async def convergence_analysis(req: ConvergenceRequest):
    """
    Run convergence analysis across increasing simulation counts.
    Returns error vs N for naive MC, antithetic, and control variates.
    """
    try:
        from mc_pricer.black_scholes import black_scholes_price
        from mc_pricer.simulation import monte_carlo_price
        from mc_pricer.variance_reduction import antithetic_price, control_variate_price

        bs_price   = black_scholes_price(req.S, req.K, req.T, req.r, req.sigma, req.option_type)
        sim_counts = [int(x) for x in np.logspace(2, 5.5, req.n_points)]

        e_naive, e_anti, e_cv = [], [], []

        for i, N in enumerate(sim_counts):
            np.random.seed(i)
            e_naive.append(abs(monte_carlo_price(req.S, req.K, req.T, req.r, req.sigma, N, req.option_type) - bs_price))
            e_anti.append(abs(antithetic_price(req.S, req.K, req.T, req.r, req.sigma, N, req.option_type) - bs_price))
            e_cv.append(abs(control_variate_price(req.S, req.K, req.T, req.r, req.sigma, N, req.option_type) - bs_price))

        return ConvergenceResponse(
            sim_counts   = sim_counts,
            errors_naive = [round(e, 6) for e in e_naive],
            errors_anti  = [round(e, 6) for e in e_anti],
            errors_cv    = [round(e, 6) for e in e_cv],
            bs_price     = round(bs_price, 4)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_paths(req: OptionRequest):
    """
    Simulate GBM stock price paths for visualization.
    Returns 50 paths + mean path for frontend charting.
    """
    try:
        n_paths = 50
        n_steps = 252
        dt      = req.T / n_steps

        np.random.seed(42)
        Z           = np.random.standard_normal((n_paths, n_steps))
        log_returns = (req.r - 0.5 * req.sigma**2) * dt + req.sigma * np.sqrt(dt) * Z
        paths       = req.S * np.exp(np.cumsum(log_returns, axis=1))
        paths       = np.hstack([np.full((n_paths, 1), req.S), paths])

        time_axis = np.linspace(0, req.T, n_steps + 1).tolist()
        mean_path = paths.mean(axis=0).tolist()

        # Simulate more paths just for final price distribution
        np.random.seed(42)
        Z_dist       = np.random.standard_normal(10000)
        S_T_dist     = req.S * np.exp((req.r - 0.5 * req.sigma**2) * req.T + req.sigma * np.sqrt(req.T) * Z_dist)

        return SimulationResponse(
            time_axis    = time_axis,
            paths        = [p.tolist() for p in paths],
            mean_path    = mean_path,
            final_prices = [round(float(s), 4) for s in S_T_dist]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))