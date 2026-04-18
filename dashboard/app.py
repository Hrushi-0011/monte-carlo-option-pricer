import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard.plots import (
    plot_option_payoff,
    plot_simulated_paths,
    plot_price_distribution,
    plot_mc_vs_bs,
    COLORS,
    LAYOUT_DEFAULTS
)
from mc_pricer.black_scholes import black_scholes_price
from mc_pricer.simulation import monte_carlo_price


def build_dashboard(
    S=100, K=100, T=1.0, r=0.05, sigma=0.20,
    n_simulations=100000, option_type='call'
):
    """
    Build the full 2x2 dashboard combining all 4 plots.

    Parameters:
        S            : Current stock price
        K            : Strike price
        T            : Time to expiry in years
        r            : Risk-free rate
        sigma        : Volatility
        n_simulations: Number of Monte Carlo simulations
        option_type  : 'call' or 'put'

    Returns:
        Plotly Figure object
    """

    np.random.seed(42)

    # ── Compute prices ──────────────────────────────────────────────────────
    bs_price = black_scholes_price(S, K, T, r, sigma, option_type)
    mc_price = monte_carlo_price(S, K, T, r, sigma, n_simulations, option_type)
    error_pct = abs(mc_price - bs_price) / bs_price * 100

    # ── Build 2x2 subplot grid ──────────────────────────────────────────────
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Option Payoff Diagram',
            'Simulated GBM Price Paths',
            'Distribution of Final Stock Prices',
            'Monte Carlo vs Black-Scholes'
        ],
        vertical_spacing=0.14,
        horizontal_spacing=0.10
    )

    # ── Plot 1: Payoff Diagram ───────────────────────────────────────────────
    payoff_fig = plot_option_payoff(K=K, premium=bs_price, option_type=option_type)
    for trace in payoff_fig.data:
        fig.add_trace(trace, row=1, col=1)

    # ── Plot 2: GBM Paths ────────────────────────────────────────────────────
    paths_fig = plot_simulated_paths(S, T, r, sigma, n_paths=150)
    for trace in paths_fig.data:
        fig.add_trace(trace, row=1, col=2)

    # ── Plot 3: Price Distribution ───────────────────────────────────────────
    dist_fig = plot_price_distribution(S, K, T, r, sigma, n_simulations, option_type)
    for trace in dist_fig.data:
        fig.add_trace(trace, row=2, col=1)

    # ── Plot 4: MC vs BS Comparison ──────────────────────────────────────────
    compare_fig = plot_mc_vs_bs(S, K, T, r, sigma, n_simulations)
    for trace in compare_fig.data:
        fig.add_trace(trace, row=2, col=2)

    # ── Global Layout ─────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor = COLORS['background'],
        plot_bgcolor  = COLORS['surface'],
        font          = dict(color=COLORS['text'], family='Inter, sans-serif'),
        height        = 900,
        title=dict(
            text=(
                f'<b>Monte Carlo Option Pricer Dashboard</b><br>'
                f'<sup>S={S} | K={K} | T={T}y | r={r:.0%} | σ={sigma:.0%} | '
                f'N={n_simulations:,} | '
                f'BS=${bs_price:.4f} | MC=${mc_price:.4f} | '
                f'Error={error_pct:.2f}%</sup>'
            ),
            font=dict(size=20, color=COLORS['primary']),
            x=0.5
        ),
        showlegend=False,
        margin=dict(l=60, r=40, t=100, b=60)
    )

    # Apply grid styling to all subplots
    fig.update_xaxes(gridcolor=COLORS['grid'], showgrid=True)
    fig.update_yaxes(gridcolor=COLORS['grid'], showgrid=True)

    # Style subplot titles
    for annotation in fig.layout.annotations:
        annotation.font.color = COLORS['primary']
        annotation.font.size  = 13

    return fig


def save_dashboard(fig, path='results/dashboard.html'):
    """Save dashboard as a standalone HTML file."""
    import os
    os.makedirs('results', exist_ok=True)
    fig.write_html(path, include_plotlyjs='cdn')
    print(f"Dashboard saved → {path}")


def show_dashboard(fig):
    """Open dashboard in browser."""
    fig.show()


if __name__ == '__main__':
    print("Building dashboard...")
    fig = build_dashboard(
        S=100, K=100, T=1.0,
        r=0.05, sigma=0.20,
        n_simulations=100000,
        option_type='call'
    )
    save_dashboard(fig)
    show_dashboard(fig)
    print("Done.")