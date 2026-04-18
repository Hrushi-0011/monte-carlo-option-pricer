import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from mc_pricer.black_scholes import black_scholes_price
from mc_pricer.simulation import monte_carlo_price
from mc_pricer.variance_reduction import antithetic_price, control_variate_price

# Color theme consistent with dashboard
COLORS = {
    'primary'    : '#00D4FF',
    'secondary'  : '#7B2FBE',
    'profit'     : '#00FF88',
    'loss'       : '#FF4444',
    'neutral'    : '#FFD700',
    'background' : '#0A0A0F',
    'surface'    : '#12121A',
    'surface2'   : '#1A1A2E',
    'text'       : '#E0E0E0',
    'grid'       : '#1E1E2E',
}


def run_convergence_analysis(S=100, K=100, T=1.0, r=0.05, sigma=0.20):
    """
    Compute convergence data for all three methods across
    increasing simulation counts.

    Returns:
        sim_counts  : list of N values tested
        errors_naive: absolute errors for naive MC
        errors_anti : absolute errors for antithetic
        errors_cv   : absolute errors for control variates
        bs_price    : Black-Scholes benchmark price
    """
    # Simulation counts — logarithmically spaced from 100 to 500,000
    sim_counts = [int(x) for x in np.logspace(2, 5.7, 40)]

    bs_price     = black_scholes_price(S, K, T, r, sigma, 'call')
    errors_naive = []
    errors_anti  = []
    errors_cv    = []

    print("Running convergence analysis...")
    for i, N in enumerate(sim_counts):
        np.random.seed(i)  # Different seed each run for honest convergence
        naive = monte_carlo_price(S, K, T, r, sigma, N, 'call')
        anti  = antithetic_price(S, K, T, r, sigma, N, 'call')
        cv    = control_variate_price(S, K, T, r, sigma, N, 'call')

        errors_naive.append(abs(naive - bs_price))
        errors_anti.append(abs(anti - bs_price))
        errors_cv.append(abs(cv - bs_price))

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/40 — N={N:,}")

    return sim_counts, errors_naive, errors_anti, errors_cv, bs_price


def plot_convergence(sim_counts, errors_naive, errors_anti, errors_cv, bs_price):
    """
    Plot convergence analysis — error vs number of simulations.
    This is the key chart that proves variance reduction works.
    """
    # Theoretical 1/sqrt(N) convergence rate line
    N_arr    = np.array(sim_counts)
    theory   = errors_naive[0] * np.sqrt(sim_counts[0]) / np.sqrt(N_arr)

    fig = go.Figure()

    # Theoretical convergence rate
    fig.add_trace(go.Scatter(
        x=sim_counts, y=theory,
        name='Theoretical 1/√N',
        line=dict(color=COLORS['neutral'], width=1.5, dash='dot'),
        hovertemplate='N=%{x:,}<br>Theory: $%{y:.4f}<extra></extra>'
    ))

    # Naive Monte Carlo
    fig.add_trace(go.Scatter(
        x=sim_counts, y=errors_naive,
        name='Naive Monte Carlo',
        line=dict(color=COLORS['loss'], width=2),
        hovertemplate='N=%{x:,}<br>Error: $%{y:.4f}<extra></extra>'
    ))

    # Antithetic Variates
    fig.add_trace(go.Scatter(
        x=sim_counts, y=errors_anti,
        name='Antithetic Variates',
        line=dict(color=COLORS['primary'], width=2),
        hovertemplate='N=%{x:,}<br>Error: $%{y:.4f}<extra></extra>'
    ))

    # Control Variates
    fig.add_trace(go.Scatter(
        x=sim_counts, y=errors_cv,
        name='Control Variates',
        line=dict(color=COLORS['profit'], width=2),
        hovertemplate='N=%{x:,}<br>Error: $%{y:.4f}<extra></extra>'
    ))

    fig.update_layout(
        paper_bgcolor = COLORS['background'],
        plot_bgcolor  = COLORS['surface'],
        font          = dict(color=COLORS['text'], family='Inter, sans-serif'),
        title=dict(
            text=(
                '<b>Convergence Analysis — Pricing Error vs Number of Simulations</b><br>'
                f'<sup>Black-Scholes Benchmark: ${bs_price:.4f} | '
                'Variance reduction methods converge faster than naive MC</sup>'
            ),
            font=dict(size=17, color=COLORS['primary']),
            x=0.5
        ),
        xaxis=dict(
            title='Number of Simulations (N)',
            type='log',
            gridcolor=COLORS['grid'],
            tickformat=',',
        ),
        yaxis=dict(
            title='Absolute Error ($)',
            type='log',
            gridcolor=COLORS['grid'],
        ),
        legend=dict(
            bgcolor=COLORS['surface2'],
            bordercolor=COLORS['grid'],
            borderwidth=1
        ),
        margin=dict(l=60, r=40, t=100, b=60),
        height=550
    )

    return fig


def plot_greeks_summary(S=100, K=100, T=1.0, r=0.05, sigma=0.20):
    """
    Bar chart comparing MC Greeks vs BS analytical Greeks.
    """
    from mc_pricer.greeks import all_greeks

    mc_g, bs_g = all_greeks(S, K, T, r, sigma, n_simulations=50000)
    greek_names = list(mc_g.keys())

    fig = make_subplots(
        rows=1, cols=5,
        subplot_titles=greek_names,
    )

    for i, name in enumerate(greek_names):
        col = i + 1

        fig.add_trace(go.Bar(
            name='Black-Scholes' if i == 0 else '',
            x=['BS'], y=[bs_g[name]],
            marker_color=COLORS['secondary'],
            showlegend=(i == 0),
            text=[f"{bs_g[name]:.4f}"],
            textposition='outside',
            textfont=dict(color=COLORS['text'], size=10)
        ), row=1, col=col)

        fig.add_trace(go.Bar(
            name='Monte Carlo' if i == 0 else '',
            x=['MC'], y=[mc_g[name]],
            marker_color=COLORS['primary'],
            showlegend=(i == 0),
            text=[f"{mc_g[name]:.4f}"],
            textposition='outside',
            textfont=dict(color=COLORS['text'], size=10)
        ), row=1, col=col)

    fig.update_layout(
        paper_bgcolor=COLORS['background'],
        plot_bgcolor =COLORS['surface'],
        font=dict(color=COLORS['text'], family='Inter, sans-serif'),
        title=dict(
            text='<b>Greeks — Monte Carlo vs Black-Scholes Analytical</b>',
            font=dict(size=17, color=COLORS['primary']),
            x=0.5
        ),
        height=450,
        barmode='group',
        legend=dict(
            bgcolor=COLORS['surface2'],
            bordercolor=COLORS['grid'],
            borderwidth=1
        ),
        margin=dict(l=40, r=40, t=80, b=40)
    )

    fig.update_xaxes(gridcolor=COLORS['grid'])
    fig.update_yaxes(gridcolor=COLORS['grid'])

    for annotation in fig.layout.annotations:
        annotation.font.color = COLORS['primary']

    return fig