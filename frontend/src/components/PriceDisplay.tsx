import { motion } from 'framer-motion'
import { PricingResult } from '../lib/api'

interface Props { result: PricingResult }

const methods = [
  { key: 'bs_price',           label: 'Black-Scholes',      color: '#FFD700' },
  { key: 'mc_price',           label: 'Monte Carlo',         color: '#00D4FF' },
  { key: 'antithetic',         label: 'Antithetic Variates', color: '#00FF88' },
  { key: 'control_variate',    label: 'Control Variates',    color: '#7B2FBE' },
  { key: 'importance_sampling',label: 'Importance Sampling', color: '#FF8C42' },
]

export default function PriceDisplay({ result }: Props) {
  return (
    <div className="glass rounded-2xl p-6" style={{ border: '1px solid var(--border)' }}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
          Pricing Results
        </h2>
        <span className="text-xs px-3 py-1 rounded-full mono"
          style={{
            background: result.error_pct < 0.5 ? 'rgba(0,255,136,0.1)' : 'rgba(255,68,68,0.1)',
            color: result.error_pct < 0.5 ? 'var(--accent-green)' : 'var(--accent-red)'
          }}>
          MC Error: {result.error_pct.toFixed(3)}%
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {methods.map((m, i) => (
          <motion.div
            key={m.key}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            className="rounded-xl p-4"
            style={{ background: 'var(--bg-surface2)' }}
          >
            <div className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>{m.label}</div>
            <div className="text-2xl font-bold mono" style={{ color: m.color }}>
              ${(result[m.key as keyof PricingResult] as number).toFixed(4)}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}