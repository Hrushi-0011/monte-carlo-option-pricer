import os
from dotenv import load_dotenv

load_dotenv()


def explain_results(pricing_data: dict, greeks_data: dict, option_type: str) -> str:
    """
    Use Groq (Llama 3) to generate a plain-English explanation of pricing results.
    """
    from groq import Groq

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    prompt = f"""
You are an expert quantitative finance educator. A user has just priced a European {option_type} option
using Monte Carlo simulation. Explain the results below in clear, engaging language.
Be concise (4-5 sentences max), insightful, and highlight what the numbers mean practically.
Avoid jargon unless you immediately explain it.

PRICING RESULTS:
- Black-Scholes (exact) price: ${pricing_data['bs_price']}
- Monte Carlo price: ${pricing_data['mc_price']}
- Pricing error: {pricing_data['error_pct']}%
- Antithetic Variates price: ${pricing_data['antithetic']}
- Control Variates price: ${pricing_data['control_variate']}

OPTION PARAMETERS:
- Stock price (S): ${pricing_data['parameters']['S']}
- Strike price (K): ${pricing_data['parameters']['K']}
- Time to expiry (T): {pricing_data['parameters']['T']} years
- Risk-free rate (r): {pricing_data['parameters']['r'] * 100}%
- Volatility (σ): {pricing_data['parameters']['sigma'] * 100}%

GREEKS:
- Delta: {greeks_data['mc_greeks'].get('Delta', 'N/A')}
- Gamma: {greeks_data['mc_greeks'].get('Gamma', 'N/A')}
- Vega: {greeks_data['mc_greeks'].get('Vega', 'N/A')}
- Theta: {greeks_data['mc_greeks'].get('Theta', 'N/A')}

Focus on: what this option is worth, how sensitive it is to market moves (Delta),
and whether variance reduction improved accuracy significantly.
"""

    response = client.chat.completions.create(
        model       = "llama-3.3-70b-versatile",
        messages    = [{"role": "user", "content": prompt}],
        max_tokens  = 300,
        temperature = 0.7
    )

    return response.choices[0].message.content