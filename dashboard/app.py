import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard.plots import (
    plot_option_payoff,
    plot_simulated_paths,
    plot_price_distribution,
    plot_mc_vs_bs,
    COLORS
)
from mc_pricer.black_scholes import black_scholes_price
from mc_pricer.simulation import monte_carlo_price
from mc_pricer.variance_reduction import compare_all_methods
from mc_pricer.greeks import all_greeks
from analysis.convergence import run_convergence_analysis


def build_dashboard(
    S=100, K=100, T=1.0, r=0.05, sigma=0.20,
    n_simulations=100000, option_type='call'
):
    """
    Build the full 3x2 professional dashboard:

    Row 1: Payoff Diagram        | GBM Simulated Paths
    Row 2: Variance Reduction    | Convergence Analysis
    Row 3: Price Distribution    | Greeks Comparison
    """

    np.random.seed(42)

    bs_price = black_scholes_price(S, K, T, r, sigma, option_type)
    mc_price = monte_carlo_price(S, K, T, r, sigma, n_simulations, option_type)
    error_pct = abs(mc_price - bs_price) / bs_price * 100

    # ── Subplot grid ──────────────────────────────────────────────────────────
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[
            'Option Payoff Diagram',
            'Simulated GBM Price Paths',
            'Variance Reduction — Method Comparison',
            'Convergence Analysis — Error vs Simulations',
            'Distribution of Final Stock Prices',
            'Greeks — Monte Carlo vs Black-Scholes',
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.10,
        row_heights=[0.33, 0.33, 0.33]
    )

    # ── ROW 1 LEFT: Payoff Diagram ────────────────────────────────────────────
    payoff_fig = plot_option_payoff(K=K, premium=bs_price, option_type=option_type)
    for trace in payoff_fig.data:
        fig.add_trace(trace, row=1, col=1)

    # ── ROW 1 RIGHT: GBM Paths ────────────────────────────────────────────────
    paths_fig = plot_simulated_paths(S, T, r, sigma, n_paths=150)
    for trace in paths_fig.data:
        fig.add_trace(trace, row=1, col=2)

    # ── ROW 2 LEFT: Variance Reduction Comparison ─────────────────────────────
    vr_results = compare_all_methods(S, K, T, r, sigma, n_simulations, option_type)
    methods     = list(vr_results.keys())
    prices      = [vr_results[m]['price'] for m in methods]
    errors      = [vr_results[m]['error_pct'] for m in methods]

    bar_colors = [
        COLORS['neutral'],    # BS exact
        COLORS['loss'],       # Naive
        COLORS['primary'],    # Antithetic
        COLORS['profit'],     # Control
        COLORS['secondary'],  # Importance
    ]

    fig.add_trace(go.Bar(
        x=methods,
        y=prices,
        name='Price by Method',
        marker_color=bar_colors,
        text=[f'${p:.4f}<br>{e:.2f}% err' for p, e in zip(prices, errors)],
        textposition='outside',
        textfont=dict(color=COLORS['text'], size=9),
        showlegend=False,
        hovertemplate='%{x}<br>Price: $%{y:.4f}<extra></extra>'
    ), row=2, col=1)

    # BS reference line
    fig.add_hline(
        y=bs_price,
        line_color=COLORS['neutral'],
        line_dash='dash',
        line_width=1.5,
        annotation_text=f'BS Exact: ${bs_price:.4f}',
        annotation_font_color=COLORS['neutral'],
        annotation_font_size=10,
        row=2, col=1
    )

    # ── ROW 2 RIGHT: Convergence Analysis ────────────────────────────────────
    print("  Computing convergence data...")
    sim_counts = [int(x) for x in np.logspace(2, 5.7, 30)]

    e_naive, e_anti, e_cv = [], [], []
    from mc_pricer.variance_reduction import antithetic_price, control_variate_price

    for i, N in enumerate(sim_counts):
        np.random.seed(i)
        e_naive.append(abs(monte_carlo_price(S, K, T, r, sigma, N, option_type) - bs_price))
        e_anti.append(abs(antithetic_price(S, K, T, r, sigma, N, option_type) - bs_price))
        e_cv.append(abs(control_variate_price(S, K, T, r, sigma, N, option_type) - bs_price))

    # Theoretical 1/sqrt(N) line
    N_arr  = np.array(sim_counts)
    theory = e_naive[0] * np.sqrt(sim_counts[0]) / np.sqrt(N_arr)

    fig.add_trace(go.Scatter(
        x=sim_counts, y=theory,
        name='1/√N Theory',
        line=dict(color=COLORS['neutral'], width=1.5, dash='dot'),
        showlegend=True,
        hovertemplate='N=%{x:,}<br>Theory: $%{y:.4f}<extra></extra>'
    ), row=2, col=2)

    fig.add_trace(go.Scatter(
        x=sim_counts, y=e_naive,
        name='Naive MC',
        line=dict(color=COLORS['loss'], width=2),
        showlegend=True,
        hovertemplate='N=%{x:,}<br>Error: $%{y:.4f}<extra></extra>'
    ), row=2, col=2)

    fig.add_trace(go.Scatter(
        x=sim_counts, y=e_anti,
        name='Antithetic',
        line=dict(color=COLORS['primary'], width=2),
        showlegend=True,
        hovertemplate='N=%{x:,}<br>Error: $%{y:.4f}<extra></extra>'
    ), row=2, col=2)

    fig.add_trace(go.Scatter(
        x=sim_counts, y=e_cv,
        name='Control Variates',
        line=dict(color=COLORS['profit'], width=2),
        showlegend=True,
        hovertemplate='N=%{x:,}<br>Error: $%{y:.4f}<extra></extra>'
    ), row=2, col=2)

    # Log scale for convergence axes
    fig.update_xaxes(type='log', row=2, col=2)
    fig.update_yaxes(type='log', row=2, col=2)

    # ── ROW 3 LEFT: Price Distribution ───────────────────────────────────────
    dist_fig = plot_price_distribution(S, K, T, r, sigma, n_simulations, option_type)
    for trace in dist_fig.data:
        fig.add_trace(trace, row=3, col=1)

    # ── ROW 3 RIGHT: Greeks Comparison ───────────────────────────────────────
    print("  Computing Greeks...")
    mc_g, bs_g = all_greeks(S, K, T, r, sigma, n_simulations=50000, option_type=option_type)

    greek_names = list(mc_g.keys())
    mc_vals     = [mc_g[g] for g in greek_names]
    bs_vals     = [bs_g[g] for g in greek_names]

    fig.add_trace(go.Bar(
        name='BS Analytical',
        x=greek_names,
        y=bs_vals,
        marker_color=COLORS['secondary'],
        text=[f'{v:.4f}' for v in bs_vals],
        textposition='outside',
        textfont=dict(color=COLORS['text'], size=9),
        showlegend=True,
    ), row=3, col=2)

    fig.add_trace(go.Bar(
        name='Monte Carlo',
        x=greek_names,
        y=mc_vals,
        marker_color=COLORS['primary'],
        text=[f'{v:.4f}' for v in mc_vals],
        textposition='outside',
        textfont=dict(color=COLORS['text'], size=9),
        showlegend=True,
    ), row=3, col=2)

    # ── Global Layout ─────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor = COLORS['background'],
        plot_bgcolor  = COLORS['surface'],
        font          = dict(color=COLORS['text'], family='Inter, sans-serif'),
        height        = 1400,
        barmode       = 'group',
        title=dict(
            text=(
                '<b>Monte Carlo Option Pricer — Full Analysis Dashboard</b><br>'
                f'<sup>S=${S} | K=${K} | T={T}yr | r={r:.0%} | σ={sigma:.0%} | '
                f'N={n_simulations:,} | '
                f'BS=${bs_price:.4f} | MC=${mc_price:.4f} | '
                f'Error={error_pct:.2f}%</sup>'
            ),
            font=dict(size=20, color=COLORS['primary']),
            x=0.5
        ),
        legend=dict(
            bgcolor     = COLORS['surface2'],
            bordercolor = COLORS['grid'],
            borderwidth = 1,
            x=0.75,
            y=0.65,
        ),
        margin=dict(l=60, r=40, t=100, b=60)
    )

    # Apply grid to all subplots
    fig.update_xaxes(gridcolor=COLORS['grid'], showgrid=True)
    fig.update_yaxes(gridcolor=COLORS['grid'], showgrid=True)

    # Style subplot titles
    for annotation in fig.layout.annotations:
        annotation.font.color = COLORS['primary']
        annotation.font.size  = 13

    return fig


def save_dashboard(fig, path='results/dashboard.html'):
    import os
    os.makedirs('results', exist_ok=True)
    fig.write_html(path, include_plotlyjs='cdn')
    print(f"  Dashboard saved → {path}")


def show_dashboard(fig):
    fig.show()


if __name__ == '__main__':
    print("Building full dashboard...")
    fig = build_dashboard()
    save_dashboard(fig)
    show_dashboard(fig)
    print("Done.")