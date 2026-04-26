import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import LandingPage from './pages/LandingPage'
import PricerPage from './pages/PricerPage'

type Page = 'landing' | 'pricer'

export default function App() {
  const [page, setPage] = useState<Page>('landing')

  return (
    <AnimatePresence mode="wait">
      {page === 'landing' ? (
        <motion.div
          key="landing"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          <LandingPage onEnter={() => setPage('pricer')} />
        </motion.div>
      ) : (
        <motion.div
          key="pricer"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          <PricerPage onBack={() => setPage('landing')} />
        </motion.div>
      )}
    </AnimatePresence>
  )
}