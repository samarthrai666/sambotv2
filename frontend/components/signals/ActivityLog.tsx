'use client';

import { LogEntry } from '../../types/trading';

interface ActivityLogProps {
  logs: LogEntry[];
  onClear: () => void;
}

export default function ActivityLog({ logs, onClear }: ActivityLogProps) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden border border-green-100 mb-6">
      <div className="border-b border-green-100 bg-gray-50 py-3 px-4 flex justify-between items-center">
        <h2 className="font-semibold text-gray-700">
          📋 Activity Log
        </h2>
        <button 
          className="text-xs text-gray-500 hover:text-gray-700"
          onClick={onClear}
        >
          Clear
        </button>
      </div>
      
      <div className="p-2 max-h-[200px] overflow-y-auto">
        {logs.length > 0 ? (
          <table className="min-w-full text-xs">
            <tbody>
              {logs.map(log => (
                <tr key={log.id} className="border-b border-gray-100 last:border-0">
                  <td className="py-2 px-3 text-gray-500 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-2 px-3 whitespace-nowrap">
                    <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                      log.type === 'info' ? 'bg-blue-500' : 
                      log.type === 'success' ? 'bg-green-500' : 
                      log.type === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                    }`}></span>
                  </td>
                  <td className="py-2 px-3 text-gray-700 w-full">
                    {log.message}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-6">
            <p className="text-gray-500">No activity yet</p>
          </div>
        )}
      </div>
    </div>
  );
}