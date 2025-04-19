// app/utils/logger.ts
import { LogEntry } from '../../types/trading';
import { Dispatch, SetStateAction } from 'react';

/**
 * Creates a logger utility that adds entries to a log state
 * @param setLogs - State setter function for logs
 * @returns Object with logging functions
 */
export const createLogger = (setLogs: Dispatch<SetStateAction<LogEntry[]>>) => {
  const maxLogs = 100; // Maximum number of logs to keep
  
  const addLog = (type: 'info' | 'success' | 'warning' | 'error', message: string) => {
    const newLog: LogEntry = {
      id: Date.now().toString(),
      type,
      message,
      timestamp: new Date().toISOString()
    };
    
    setLogs(prevLogs => [newLog, ...prevLogs.slice(0, maxLogs - 1)]); // Keep last 100 logs
    return newLog;
  };
  
  return {
    info: (message: string) => addLog('info', message),
    success: (message: string) => addLog('success', message),
    warning: (message: string) => addLog('warning', message),
    error: (message: string) => addLog('error', message),
    clear: () => setLogs([])
  };
};