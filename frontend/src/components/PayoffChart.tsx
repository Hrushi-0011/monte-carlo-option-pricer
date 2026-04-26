import { useMemo } from 'react'

interface Props {
  K: number
  premium: number
  optionType: 'call' | 'put'
}

export default function PayoffChart({ K, premium, optionType }: Props) {
  const { S_range, gross, net } = useMemo(() => {
    const S_range = Array.from({ length: 300 }, (_, i) => K * 0.5 + i * (K * 1.0 / 299))
    const gross   = S_range.map(s => Math.max(optionType === 'call' ? s - K : K - s, 0))
    const net     = gross.map(g => g - premium)
    return { S_range, gross, net }
  }, [K, premium, optionType])

  const width  = 600
  const height = 280
  const padL   = 55, padR = 20, padT = 40, padB = 50
  const chartW = width - padL - padR
  const chartH = height - padT - padB

  const allY  = [...gross, ...net]
  const minY  = Math.min(...allY)
  const maxY  = Math.max(...allY)
  const minX  = S_range[0]
  const maxX  = S_range[S_range.length - 1]

  const toX = (s: number) => padL + ((s - minX) / (maxX - minX)) * chartW
  const toY = (v: number) => padT + chartH - ((v - minY) / (maxY - minY + 1e-9)) * chartH

  const polyline = (arr: number[]) =>
    S_range.map((s, i) => `${toX(s)},${toY(arr[i])}`).join(' ')

  return (
    <div className="glass rounded-2xl p-4" style={{ border: '1px solid var(--border)' }}>
      <p className="text-sm font-semibold mb-2" style={{ color: 'var(--accent-cyan)' }}>
        {optionType.toUpperCase()} Payoff Diagram
      </p>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" style={{ fontFamily: 'Inter, sans-serif' }}>
        {/* Background */}
        <rect x={padL} y={padT} width={chartW} height={chartH} fill="#12121A" rx="4" />

        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map(t => (
          <line key={t}
            x1={padL} x2={padL + chartW}
            y1={padT + t * chartH} y2={padT + t * chartH}
            stroke="#1E1E2E" strokeWidth="1"
          />
        ))}

        {/* Zero line */}
        <line
          x1={padL} x2={padL + chartW}
          y1={toY(0)} y2={toY(0)}
          stroke="#E0E0E0" strokeWidth="0.8" strokeDasharray="4,3" opacity="0.4"
        />

        {/* Strike line */}
        <line
          x1={toX(K)} x2={toX(K)}
          y1={padT} y2={padT + chartH}
          stroke="#FFD700" strokeWidth="1.5" strokeDasharray="5,3"
        />
        <text x={toX(K) + 4} y={padT + 14} fill="#FFD700" fontSize="10">K={K}</text>

        {/* Gross payoff */}
        <polyline points={polyline(gross)} fill="none" stroke="#00D4FF" strokeWidth="2.5" />

        {/* Net profit */}
        <polyline points={polyline(net)} fill="none" stroke="#00FF88" strokeWidth="2.5" strokeDasharray="6,3" />

        {/* Axes */}
        <line x1={padL} x2={padL + chartW} y1={padT + chartH} y2={padT + chartH} stroke="#E0E0E0" strokeWidth="0.5" />
        <line x1={padL} x2={padL} y1={padT} y2={padT + chartH} stroke="#E0E0E0" strokeWidth="0.5" />

        {/* X axis labels */}
        {[0, 0.25, 0.5, 0.75, 1].map(t => {
          const val = minX + t * (maxX - minX)
          return (
            <text key={t} x={toX(val)} y={padT + chartH + 16} textAnchor="middle" fill="#8892A4" fontSize="10">
              ${val.toFixed(0)}
            </text>
          )
        })}

        {/* Y axis labels */}
        {[0, 0.5, 1].map(t => {
          const val = minY + t * (maxY - minY)
          return (
            <text key={t} x={padL - 6} y={toY(val) + 4} textAnchor="end" fill="#8892A4" fontSize="10">
              ${val.toFixed(0)}
            </text>
          )
        })}

        {/* Legend */}
        <line x1={padL + 10} x2={padL + 30} y1={padT + 16} y2={padT + 16} stroke="#00D4FF" strokeWidth="2" />
        <text x={padL + 34} y={padT + 20} fill="#E0E0E0" fontSize="10">Gross Payoff</text>
        <line x1={padL + 110} x2={padL + 130} y1={padT + 16} y2={padT + 16} stroke="#00FF88" strokeWidth="2" strokeDasharray="4,2" />
        <text x={padL + 134} y={padT + 20} fill="#E0E0E0" fontSize="10">Net Profit</text>
      </svg>
    </div>
  )
}