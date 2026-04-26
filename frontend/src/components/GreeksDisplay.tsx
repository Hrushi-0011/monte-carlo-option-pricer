import { motion } from 'framer-motion'
import { GreeksResult } from '../lib/api'

interface Props { result: GreeksResult }

const greekInfo: Record<string, { symbol: string, desc: string }> = {
  Delta: { symbol: 'Δ', desc: 'Price sensitivity to S' },
  Gamma: { symbol: 'Γ', desc: 'Delta sensitivity to S' },
  Vega:  { symbol: 'ν', desc: 'Sensitivity to volatility' },
  Theta: { symbol: 'Θ', desc: 'Daily time decay' },
  Rho:   { symbol: 'ρ', desc: 'Sensitivity to rates' },
}

export default function GreeksDisplay({ result }: Props) {
  return (
    <div className="glass rounded-2xl p-6" style={{ border: '1px solid var(--border)' }}>
      <h2 className="font-semibold text-lg mb-6" style={{ color: 'var(--text-primary)' }}>
        Greeks
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {Object.entries(result.mc_greeks).map(([greek, mcVal], i) => {
          const bsVal  = result.bs_greeks[greek]
          const errPct = Math.abs((mcVal - bsVal) / (Math.abs(bsVal) + 1e-10)) * 100
          const info   = greekInfo[greek]

          return (
            <motion.div
              key={greek}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="rounded-xl p-4 text-center"
              style={{ background: 'var(--bg-surface2)' }}
            >
              <div className="text-2xl font-bold mb-1" style={{ color: 'var(--accent-purple)' }}>
                {info.symbol}
              </div>
              <div className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>{greek}</div>
              <div className="text-lg font-bold mono" style={{ color: 'var(--accent-cyan)' }}>
                {mcVal.toFixed(4)}
              </div>
              <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                BS: {bsVal.toFixed(4)}
              </div>
              <div className="text-xs mt-1" style={{
                color: errPct < 1 ? 'var(--accent-green)' : 'var(--accent-red)'
              }}>
                {errPct.toFixed(2)}% err
              </div>
              <div className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>{info.desc}</div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}