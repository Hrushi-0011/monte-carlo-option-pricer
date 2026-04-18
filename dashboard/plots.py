import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Color Theme ─────────────────────────────────────────────────────────────
COLORS = {
    'primary'    : '#00D4FF',   # Cyan
    'secondary'  : '#7B2FBE',   # Purple
    'profit'     : '#00FF88',   # Green
    'loss'       : '#FF4444',   # Red
    'neutral'    : '#FFD700',   # Gold
    'background' : '#0A0A0F',   # Near black
    'surface'    : '#12121A',   # Dark surface
    'surface2'   : '#1A1A2E',   # Slightly lighter
    'text'       : '#E0E0E0',   # Light grey
    'grid'       : '#1E1E2E',   # Subtle grid
}

LAYOUT_DEFAULTS = dict(
    paper_bgcolor = COLORS['background'],
    plot_bgcolor  = COLORS['surface'],
    font          = dict(color=COLORS['text'], family='Inter, sans-serif'),
    margin        = dict(l=60, r=40, t=60, b=60),
    xaxis         = dict(gridcolor=COLORS['grid'], showgrid=True),
    yaxis         = dict(gridcolor=COLORS['grid'], showgrid=True),
)


def plot_option_payoff(K=100, premium=10, option_type='call'):
    """
    Plot option payoff diagram at expiry vs stock price.
    Shows both gross payoff and net profit (after premium paid).
    """
    S_range = np.linspace(50, 150, 500)

    if option_type == 'call':
        gross_payoff = np.maximum(S_range - K, 0)
    else:
        gross_payoff = np.maximum(K - S_range, 0)

    net_profit = gross_payoff - premium

    fig = go.Figure()

    # Gross payoff line
    fig.add_trace(go.Scatter(
        x=S_range, y=gross_payoff,
        name='Gross Payoff',
        line=dict(color=COLORS['primary'], width=2.5),
        hovertemplate='Stock: $%{x:.2f}<br>Payoff: $%{y:.2f}<extra></extra>'
    ))

    # Net profit line
    fig.add_trace(go.Scatter(
        x=S_range, y=net_profit,
        name='Net Profit',
        line=dict(color=COLORS['profit'], width=2.5, dash='dash'),
        hovertemplate='Stock: $%{x:.2f}<br>Net: $%{y:.2f}<extra></extra>'
    ))

    # Zero line
    fig.add_hline(y=0, line_color=COLORS['text'], line_dash='dot', opacity=0.4)

    # Strike price line
    fig.add_vline(
        x=K,
        line_color=COLORS['neutral'],
        line_dash='dash',
        annotation_text=f'Strike K={K}',
        annotation_font_color=COLORS['neutral']
    )

    # Shade profit zone green, loss zone red
    profit_mask = net_profit >= 0
    fig.add_trace(go.Scatter(
        x=np.concatenate([S_range[profit_mask], S_range[profit_mask][::-1]]),
        y=np.concatenate([net_profit[profit_mask], np.zeros(profit_mask.sum())]),
        fill='toself',
        fillcolor='rgba(0, 255, 136, 0.08)',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text=f'European {option_type.capitalize()} Option — Payoff Diagram',
            font=dict(size=18, color=COLORS['primary'])
        ),
        xaxis_title='Stock Price at Expiry ($)',
        yaxis_title='Profit / Loss ($)',
        legend=dict(
            bgcolor=COLORS['surface2'],
            bordercolor=COLORS['grid'],
            borderwidth=1
        )
    )

    return fig


def plot_simulated_paths(S, T, r, sigma, n_paths=200, n_steps=252):
    """
    Plot simulated GBM stock price paths.
    Shows a sample of paths + the mean path.
    """
    from mc_pricer.simulation import simulate_gbm

    dt = T / n_steps
    time_axis = np.linspace(0, T, n_steps + 1)

    # Simulate full paths (not just final price)
    Z = np.random.standard_normal((n_paths, n_steps))
    log_returns = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    paths = S * np.exp(np.cumsum(log_returns, axis=1))
    paths = np.hstack([np.full((n_paths, 1), S), paths])

    fig = go.Figure()

    # Plot individual paths (semi-transparent)
    for i in range(min(n_paths, 100)):
        fig.add_trace(go.Scatter(
            x=time_axis, y=paths[i],
            mode='lines',
            line=dict(color=COLORS['primary'], width=0.5),
            opacity=0.15,
            showlegend=False,
            hoverinfo='skip'
        ))

    # Plot mean path
    mean_path = paths.mean(axis=0)
    fig.add_trace(go.Scatter(
        x=time_axis, y=mean_path,
        mode='lines',
        name='Mean Path',
        line=dict(color=COLORS['neutral'], width=2.5),
        hovertemplate='Time: %{x:.2f}y<br>Price: $%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text=f'Simulated GBM Paths — {n_paths} Scenarios',
            font=dict(size=18, color=COLORS['primary'])
        ),
        xaxis_title='Time (Years)',
        yaxis_title='Stock Price ($)',
    )

    return fig


def plot_price_distribution(S, K, T, r, sigma, n_simulations=100000, option_type='call'):
    """
    Plot the distribution of simulated final stock prices
    with strike price marked.
    """
    from mc_pricer.simulation import simulate_gbm

    S_T = simulate_gbm(S, T, r, sigma, n_simulations)

    if option_type == 'call':
        itm = S_T[S_T > K]
        otm = S_T[S_T <= K]
    else:
        itm = S_T[S_T < K]
        otm = S_T[S_T >= K]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=otm,
        name='Out of the Money',
        marker_color=COLORS['loss'],
        opacity=0.6,
        nbinsx=100,
        hovertemplate='Price: $%{x:.2f}<br>Count: %{y}<extra></extra>'
    ))

    fig.add_trace(go.Histogram(
        x=itm,
        name='In the Money',
        marker_color=COLORS['profit'],
        opacity=0.6,
        nbinsx=100,
        hovertemplate='Price: $%{x:.2f}<br>Count: %{y}<extra></extra>'
    ))

    fig.add_vline(
        x=K,
        line_color=COLORS['neutral'],
        line_dash='dash',
        annotation_text=f'Strike K={K}',
        annotation_font_color=COLORS['neutral']
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        barmode='overlay',
        title=dict(
            text=f'Distribution of Final Stock Prices ({n_simulations:,} simulations)',
            font=dict(size=18, color=COLORS['primary'])
        ),
        xaxis_title='Final Stock Price ($)',
        yaxis_title='Frequency',
        legend=dict(
            bgcolor=COLORS['surface2'],
            bordercolor=COLORS['grid'],
            borderwidth=1
        )
    )

    return fig


def plot_mc_vs_bs(S, K, T, r, sigma, n_simulations=100000):
    """
    Bar chart comparing Monte Carlo vs Black-Scholes prices
    for both call and put.
    """
    from mc_pricer.black_scholes import black_scholes_price
    from mc_pricer.simulation import monte_carlo_price

    np.random.seed(42)

    results = {}
    for opt in ['call', 'put']:
        results[opt] = {
            'bs' : black_scholes_price(S, K, T, r, sigma, opt),
            'mc' : monte_carlo_price(S, K, T, r, sigma, n_simulations, opt)
        }

    categories = ['Call Option', 'Put Option']
    bs_values  = [results['call']['bs'], results['put']['bs']]
    mc_values  = [results['call']['mc'], results['put']['mc']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Black-Scholes (Exact)',
        x=categories,
        y=bs_values,
        marker_color=COLORS['secondary'],
        text=[f'${v:.4f}' for v in bs_values],
        textposition='outside',
        textfont=dict(color=COLORS['text'])
    ))

    fig.add_trace(go.Bar(
        name='Monte Carlo',
        x=categories,
        y=mc_values,
        marker_color=COLORS['primary'],
        text=[f'${v:.4f}' for v in mc_values],
        textposition='outside',
        textfont=dict(color=COLORS['text'])
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        barmode='group',
        title=dict(
            text='Monte Carlo vs Black-Scholes Price Comparison',
            font=dict(size=18, color=COLORS['primary'])
        ),
        yaxis_title='Option Price ($)',
        legend=dict(
            bgcolor=COLORS['surface2'],
            bordercolor=COLORS['grid'],
            borderwidth=1
        )
    )

    return fig