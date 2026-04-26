import axios from 'axios'

const BASE_URL =
  (import.meta as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
})

export interface OptionParams {
  S: number
  K: number
  T: number
  r: number
  sigma: number
  N: number
  option_type: 'call' | 'put'
}

export interface PricingResult {
  bs_price: number
  mc_price: number
  antithetic: number
  control_variate: number
  importance_sampling: number
  error_pct: number
  option_type: string
  parameters: Record<string, number>
}

export interface GreeksResult {
  mc_greeks: Record<string, number>
  bs_greeks: Record<string, number>
  parameters: Record<string, number>
}

export interface ConvergenceResult {
  sim_counts: number[]
  errors_naive: number[]
  errors_anti: number[]
  errors_cv: number[]
  bs_price: number
}

export interface SimulationResult {
  time_axis: number[]
  paths: number[][]
  mean_path: number[]
  final_prices: number[]
}

export const priceOption = async (params: OptionParams): Promise<PricingResult> => {
  const { data } = await api.post('/price/', params)
  return data
}

export const computeGreeks = async (params: OptionParams): Promise<GreeksResult> => {
  const { data } = await api.post('/greeks/', params)
  return data
}

export const runConvergence = async (params: Omit<OptionParams, 'N'>): Promise<ConvergenceResult> => {
  const { data } = await api.post('/analysis/convergence', { ...params, n_points: 20 })
  return data
}

export const simulatePaths = async (params: OptionParams): Promise<SimulationResult> => {
  const { data } = await api.post('/analysis/simulate', params)
  return data
}

export const getExplanation = async (params: OptionParams): Promise<string> => {
  const { data } = await api.post('/explain', params)
  return data.explanation
}