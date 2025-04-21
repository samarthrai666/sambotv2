// hooks/useAvailableSignals.ts
import { useState, useEffect, useCallback } from 'react'
import { Signal } from '../types/trading'
import { fetchAvailableSignals, refreshSignalAnalysis } from '../../app/services/api';

export const useAvailableSignals = (refreshInterval = 5000) => {
  const [signals, setSignals] = useState<Signal[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const refreshSignals = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Step 1: Fetch base signals
      const availableSignals = await fetchAvailableSignals()

      // Step 2: Refresh signals with current market data
      const updatedSignals = await refreshSignalAnalysis(availableSignals)

      setSignals(updatedSignals)
    } catch (err) {
      console.error('🚨 Error refreshing signals:', err)
      setError('Failed to refresh signals')
      setSignals([]) // optional: clear stale data
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshSignals()
    const intervalId = setInterval(refreshSignals, refreshInterval)
    return () => clearInterval(intervalId)
  }, [refreshSignals, refreshInterval])

  return {
    signals,
    isLoading,
    error,
    refreshSignals,
  }
}
