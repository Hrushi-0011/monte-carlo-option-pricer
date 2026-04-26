import { motion } from 'framer-motion'
import { Brain, Sparkles } from 'lucide-react'

interface Props { explanation: string }

export default function AIPanel({ explanation }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6"
      style={{ border: '1px solid rgba(123,47,190,0.3)' }}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: 'rgba(123,47,190,0.2)', color: 'var(--accent-purple)' }}>
          <Brain size={18} />
        </div>
        <div>
          <h2 className="font-semibold" style={{ color: 'var(--text-primary)' }}>AI Analysis</h2>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Powered by Llama 3.3 70B</p>
        </div>
        <Sparkles size={16} className="ml-auto" style={{ color: 'var(--accent-purple)' }} />
      </div>
      <p className="text-sm leading-relaxed" style={{ color: 'var(--text-primary)' }}>
        {explanation}
      </p>
    </motion.div>
  )
}