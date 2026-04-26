import { motion } from 'framer-motion'
import { ArrowRight, BarChart3, Brain, Zap, Shield, TrendingUp } from 'lucide-react'

interface Props {
  onEnter: () => void
}

const features = [
  {
    icon: <BarChart3 size={22} />,
    title: 'Monte Carlo Engine',
    desc: '100,000 simulated paths using Geometric Brownian Motion for precise option pricing.'
  },
  {
    icon: <Zap size={22} />,
    title: 'Variance Reduction',
    desc: 'Antithetic variates, control variates, and importance sampling — 50% fewer simulations needed.'
  },
  {
    icon: <TrendingUp size={22} />,
    title: 'Greeks Estimation',
    desc: 'Delta, Gamma, Vega, Theta, Rho via finite differences — all within 0.5% of analytical values.'
  },
  {
    icon: <Shield size={22} />,
    title: 'Black-Scholes Benchmark',
    desc: 'Every result validated against the exact analytical solution in real time.'
  },
  {
    icon: <Brain size={22} />,
    title: 'AI Explanations',
    desc: 'Llama 3 explains what your results mean in plain English — no quant PhD required.'
  },
  {
    icon: <BarChart3 size={22} />,
    title: 'Convergence Analysis',
    desc: 'Visual proof of how variance reduction achieves higher accuracy with fewer simulations.'
  },
]

const stats = [
  { value: '< 0.25%', label: 'Pricing Error' },
  { value: '100K',    label: 'Simulations' },
  { value: '5',       label: 'Greeks Computed' },
  { value: '3',       label: 'VR Techniques' },
]

export default function LandingPage({ onEnter }: Props) {
  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>

      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 glass border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
          <span className="gradient-text font-bold text-xl mono">mc_pricer</span>
          <div className="flex items-center gap-6">
            
              <a href="https://github.com"
              className="text-sm font-medium transition-colors hover:opacity-80"
              style={{ color: 'var(--text-muted)' }}
            >
              GitHub
            </a>
            <button
              onClick={onEnter}
              className="px-5 py-2 rounded-lg text-sm font-semibold transition-all hover:opacity-90"
              style={{
                background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))',
                color: '#fff'
              }}
            >
              Launch App
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
        {/* Glow blobs */}
        <div className="absolute top-1/3 left-1/4 w-80 h-80 rounded-full opacity-10 blur-3xl pointer-events-none"
          style={{ background: 'var(--accent-cyan)' }} />
        <div className="absolute bottom-1/3 right-1/4 w-80 h-80 rounded-full opacity-10 blur-3xl pointer-events-none"
          style={{ background: 'var(--accent-purple)' }} />

        <div className="max-w-4xl mx-auto px-8 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
          >
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium mb-10 glass"
              style={{ color: 'var(--accent-cyan)', border: '1px solid rgba(0,212,255,0.2)' }}>
              <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: 'var(--accent-green)' }} />
              Production-Grade Quantitative Finance Engine
            </div>

            <h1 className="text-7xl md:text-8xl font-bold mb-6 leading-tight tracking-tight">
              <span className="gradient-text">Monte Carlo</span>
              <br />
              <span style={{ color: 'var(--text-primary)' }}>Option Pricer</span>
            </h1>

            <p className="text-xl mb-12 max-w-xl mx-auto leading-relaxed" style={{ color: 'var(--text-muted)' }}>
              Price European options with institutional-grade Monte Carlo simulation.
              Variance reduction, Greeks, convergence analysis — all in one place.
            </p>

            <div className="flex items-center justify-center gap-4 flex-wrap">
              <motion.button
                onClick={onEnter}
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.97 }}
                className="flex items-center gap-2 px-8 py-4 rounded-xl font-semibold text-base glow-cyan"
                style={{
                  background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))',
                  color: '#fff'
                }}
              >
                Launch Pricer <ArrowRight size={18} />
              </motion.button>

              <motion.a
                href="https://github.com"
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.97 }}
                className="flex items-center gap-2 px-8 py-4 rounded-xl font-semibold text-base glass"
                style={{ color: 'var(--text-primary)', border: '1px solid var(--border)' }}
              >
                View Source
              </motion.a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 border-y" style={{ borderColor: 'var(--border)', background: 'var(--bg-surface)' }}>
        <div className="max-w-4xl mx-auto px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-10">
            {stats.map((s, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <div className="text-4xl font-bold mono gradient-text">{s.value}</div>
                <div className="text-sm mt-2" style={{ color: 'var(--text-muted)' }}>{s.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-28">
        <div className="max-w-7xl mx-auto px-8">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
              Everything you need to price options
            </h2>
            <p style={{ color: 'var(--text-muted)' }}>
              Built on rigorous mathematical foundations. Validated against Black-Scholes analytical solutions.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                whileHover={{ y: -5 }}
                className="rounded-2xl p-6 transition-all cursor-default"
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border)',
                }}
              >
                <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4"
                  style={{ background: 'rgba(0,212,255,0.08)', color: 'var(--accent-cyan)' }}>
                  {f.icon}
                </div>
                <h3 className="font-semibold text-base mb-2" style={{ color: 'var(--text-primary)' }}>
                  {f.title}
                </h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>
                  {f.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 text-center" style={{ background: 'var(--bg-surface)' }}>
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="max-w-xl mx-auto px-8"
        >
          <h2 className="text-4xl font-bold mb-4 gradient-text">Ready to price options?</h2>
          <p className="mb-8" style={{ color: 'var(--text-muted)' }}>
            Enter your parameters and get institutional-grade results in seconds.
          </p>
          <motion.button
            onClick={onEnter}
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            className="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-semibold text-base glow-cyan"
            style={{
              background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))',
              color: '#fff'
            }}
          >
            Launch Pricer <ArrowRight size={18} />
          </motion.button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-6 border-t text-center" style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
        <p className="text-xs mono">mc_pricer v1.0.0 — Built with Python, FastAPI, React, Tailwind</p>
      </footer>
    </div>
  )
}