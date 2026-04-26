import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Play, Loader2 } from 'lucide-react'
import { OptionParams, PricingResult, GreeksResult, priceOption, computeGreeks, getExplanation } from '../lib/api'
import PriceDisplay from '../components/PriceDisplay'
import GreeksDisplay from '../components/GreeksDisplay'
import AIPanel from '../components/AIPanel'
import PayoffChart from '../components/PayoffChart'

interface Props { onBack: () => void }

const DEFAULT_PARAMS: OptionParams = {
  S: 100, K: 100, T: 1.0,
  r: 0.05, sigma: 0.20,
  N: 100000, option_type: 'call'
}

const SLIDERS = [
  { key: 'S',     label: 'Stock Price (S)',  min: 50,   max: 500,    step: 1,    fmt: (v: number) => `$${v}` },
  { key: 'K',     label: 'Strike Price (K)', min: 50,   max: 500,    step: 1,    fmt: (v: number) => `$${v}` },
  { key: 'T',     label: 'Expiry (years)',   min: 0.1,  max: 5,      step: 0.1,  fmt: (v: number) => `${v.toFixed(1)}y` },
  { key: 'r',     label: 'Risk-free Rate',   min: 0.01, max: 0.15,   step: 0.01, fmt: (v: number) => `${(v*100).toFixed(0)}%` },
  { key: 'sigma', label: 'Volatility (σ)',   min: 0.05, max: 1.0,    step: 0.01, fmt: (v: number) => `${(v*100).toFixed(0)}%` },
]

export default function PricerPage({ onBack }: Props) {
  const [params, setParams]           = useState<OptionParams>(DEFAULT_PARAMS)
  const [pricing, setPricing]         = useState<PricingResult | null>(null)
  const [greeks, setGreeks]           = useState<GreeksResult | null>(null)
  const [explanation, setExplanation] = useState<string>('')
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState<string>('')

  const handleRun = async () => {
    setLoading(true)
    setError('')
    setExplanation('')
    try {
      const [p, g] = await Promise.all([priceOption(params), computeGreeks(params)])
      setPricing(p)
      setGreeks(g)
      getExplanation(params).then(setExplanation).catch(() => {})
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const update = (key: keyof OptionParams) => (val: any) =>
    setParams(p => ({ ...p, [key]: val }))

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>

      {/* Navbar */}
      <nav className="sticky top-0 z-50 glass border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-sm font-medium transition-opacity hover:opacity-70"
            style={{ color: 'var(--text-muted)' }}
          >
            <ArrowLeft size={15} /> Back
          </button>
          <span className="gradient-text font-bold text-xl mono">mc_pricer</span>
          <div style={{ width: 60 }} />
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-8 py-10">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-3xl font-bold gradient-text mb-1">Option Pricer</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Configure parameters and run the Monte Carlo engine
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">

          {/* ── Input Panel ─────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="rounded-2xl p-6 sticky top-24"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
          >
            <h2 className="font-semibold text-base mb-6" style={{ color: 'var(--text-primary)' }}>
              Parameters
            </h2>

            {/* Option Type */}
            <div className="mb-6">
              <label className="text-xs font-medium tracking-widest mb-3 block" style={{ color: 'var(--text-muted)' }}>
                OPTION TYPE
              </label>
              <div className="grid grid-cols-2 gap-2">
                {(['call', 'put'] as const).map(t => (
                  <button
                    key={t}
                    onClick={() => update('option_type')(t)}
                    className="py-2.5 rounded-lg text-sm font-semibold capitalize transition-all"
                    style={{
                      background: params.option_type === t
                        ? 'linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))'
                        : 'var(--bg-surface2)',
                      color: params.option_type === t ? '#fff' : 'var(--text-muted)',
                      border: params.option_type === t ? 'none' : '1px solid var(--border)'
                    }}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {/* Sliders */}
            {SLIDERS.map(({ key, label, min, max, step, fmt }) => (
              <div key={key} className="mb-5">
                <div className="flex justify-between items-center mb-2">
                  <label className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>
                    {label}
                  </label>
                  <span className="text-sm font-bold mono" style={{ color: 'var(--accent-cyan)' }}>
                    {fmt(params[key as keyof OptionParams] as number)}
                  </span>
                </div>
                <input
                  type="range" min={min} max={max} step={step}
                  value={params[key as keyof OptionParams] as number}
                  onChange={e => update(key as keyof OptionParams)(parseFloat(e.target.value))}
                  className="w-full cursor-pointer"
                />
              </div>
            ))}

            {/* Simulations */}
            <div className="mb-7">
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>
                  SIMULATIONS (N)
                </label>
                <span className="text-sm font-bold mono" style={{ color: 'var(--accent-cyan)' }}>
                  {params.N.toLocaleString()}
                </span>
              </div>
              <input
                type="range" min={10000} max={500000} step={10000}
                value={params.N}
                onChange={e => update('N')(parseInt(e.target.value))}
                className="w-full cursor-pointer"
              />
            </div>

            {/* Run Button */}
            <motion.button
              onClick={handleRun}
              disabled={loading}
              whileHover={{ scale: loading ? 1 : 1.02 }}
              whileTap={{ scale: loading ? 1 : 0.98 }}
              className="w-full py-3.5 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all"
              style={{
                background: loading
                  ? 'var(--bg-surface2)'
                  : 'linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))',
                color: loading ? 'var(--text-muted)' : '#fff',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading
                ? <><Loader2 size={17} className="animate-spin" /> Computing...</>
                : <><Play size={17} /> Run Pricer</>
              }
            </motion.button>

            {error && (
              <p className="text-xs mt-3 text-center" style={{ color: 'var(--accent-red)' }}>
                ⚠ {error}
              </p>
            )}
          </motion.div>

          {/* ── Results Panel ───────────────────────────── */}
          <div className="lg:col-span-2 flex flex-col gap-5">

            {/* Payoff Chart — always visible */}
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
              <PayoffChart
                K={params.K}
                premium={pricing?.bs_price ?? 10}
                optionType={params.option_type}
              />
            </motion.div>

            <AnimatePresence>
              {pricing && (
                <motion.div
                  key="pricing"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  <PriceDisplay result={pricing} />
                </motion.div>
              )}

              {greeks && (
                <motion.div
                  key="greeks"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  <GreeksDisplay result={greeks} />
                </motion.div>
              )}

              {explanation && (
                <motion.div
                  key="ai"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <AIPanel explanation={explanation} />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Empty state */}
            {!pricing && !loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="rounded-2xl p-12 text-center"
                style={{ background: 'var(--bg-surface)', border: '1px dashed var(--border)' }}
              >
                <p className="text-4xl mb-3">⚡</p>
                <p className="font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                  Ready to compute
                </p>
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  Set your parameters and click Run Pricer
                </p>
              </motion.div>
            )}

          </div>
        </div>
      </div>
    </div>
  )
}