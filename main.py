import numpy as np
from mc_pricer.black_scholes import black_scholes_price
from mc_pricer.simulation import monte_carlo_price
from mc_pricer.variance_reduction import compare_all_methods
from mc_pricer.greeks import all_greeks
from analysis.convergence import run_convergence_analysis, plot_convergence, plot_greeks_summary
from dashboard.app import build_dashboard, save_dashboard, show_dashboard
import os

os.makedirs('results', exist_ok=True)

S, K, T, r, sigma, N = 100, 100, 1.0, 0.05, 0.20, 100000
np.random.seed(42)

# ── Variance Reduction Comparison ───────────────────────────────────────────
print("=" * 65)
print("   VARIANCE REDUCTION COMPARISON — CALL OPTION")
print("=" * 65)
print(f"  {'Method':<30} {'Price':>10} {'Error':>10} {'Error %':>10}")
print("  " + "-" * 61)

results = compare_all_methods(S, K, T, r, sigma, N, 'call')
for method, data in results.items():
    print(f"  {method:<30} ${data['price']:>9.4f} ${data['error']:>9.4f} {data['error_pct']:>9.2f}%")

print("=" * 65)

# ── Greeks ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("   GREEKS COMPARISON — CALL OPTION")
print("=" * 65)
print(f"  {'Greek':<10} {'MC Estimate':>15} {'BS Analytical':>15} {'Error %':>10}")
print("  " + "-" * 55)

mc_g, bs_g = all_greeks(S, K, T, r, sigma, n_simulations=50000)
for greek in mc_g:
    mc_val = mc_g[greek]
    bs_val = bs_g[greek]
    err    = abs(mc_val - bs_val) / (abs(bs_val) + 1e-10) * 100
    print(f"  {greek:<10} {mc_val:>15.6f} {bs_val:>15.6f} {err:>9.2f}%")

print("=" * 65)

# ── Convergence Analysis ──────────────────────────────────────────────────────
print("\nRunning convergence analysis (this takes ~30 seconds)...")
sim_counts, e_naive, e_anti, e_cv, bs_price = run_convergence_analysis(S, K, T, r, sigma)

conv_fig = plot_convergence(sim_counts, e_naive, e_anti, e_cv, bs_price)
conv_fig.write_html('results/convergence.html', include_plotlyjs='cdn')
print("Convergence plot saved → results/convergence.html")

# ── Greeks Plot ───────────────────────────────────────────────────────────────
greeks_fig = plot_greeks_summary(S, K, T, r, sigma)
greeks_fig.write_html('results/greeks.html', include_plotlyjs='cdn')
print("Greeks plot saved → results/greeks.html")

# ── Dashboard ─────────────────────────────────────────────────────────────────
print("\nBuilding main dashboard...")
fig = build_dashboard(S, K, T, r, sigma, N, option_type='call')
save_dashboard(fig)
show_dashboard(fig)
print("\nAll done. Check results/ folder for all outputs.")