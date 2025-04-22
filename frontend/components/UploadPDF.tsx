// /components/UploadPDF.tsx
import { useState } from 'react'

export default function UploadPDF() {
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [analysis, setAnalysis] = useState<any>(null)

  const handleUpload = async () => {
    if (!file) {
      setStatus('Please select a file first')
      return
    }

    setIsUploading(true)
    setStatus('Uploading and analyzing PDF...')
    setAnalysis(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Make sure this URL matches your backend server
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${API_URL}/upload-pdf`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        throw new Error(`Server responded with status: ${res.status}`)
      }

      const data = await res.json()
      console.log('Response data:', data)
      
      if (data.status === 'success') {
        setStatus('PDF analysis completed successfully!')
        setAnalysis(data.analysis)
      } else {
        setStatus(data.message || 'Upload failed with unknown error')
      }
    } catch (error) {
      console.error('Upload error:', error)
      setStatus(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-green-100 p-3 mt-6">
      <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
        <span className="text-lg mr-1">📊</span>
        Pre-Market Analysis PDF
      </h3>
      
      <div className="flex items-center space-x-2">
        <label className="flex-1">
          <div className="flex items-center justify-center px-4 py-2 border border-gray-300 border-dashed rounded-md bg-gray-50 hover:bg-gray-100 cursor-pointer">
            <span className="text-xs text-gray-500">
              {file ? file.name : 'Select PDF report'}
            </span>
          </div>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="hidden"
          />
        </label>
        
        <button
          onClick={handleUpload}
          disabled={isUploading || !file}
          className={`px-3 py-2 rounded-md text-xs font-medium text-white ${
            isUploading || !file
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700'
          }`}
        >
          {isUploading ? 'Processing...' : 'Upload'}
        </button>
      </div>
      
      {status && (
        <div className={`mt-2 text-xs rounded-md p-2 ${
          status.includes('success') 
            ? 'bg-green-50 text-green-700' 
            : status.includes('Uploading')
              ? 'bg-blue-50 text-blue-700'
              : 'bg-red-50 text-red-700'
        }`}>
          {status}
        </div>
      )}

      {/* Display analysis results if available */}
      {analysis && analysis.gpt_response && (
        <div className="mt-3 p-3 bg-green-50 rounded-md border border-green-100 text-xs">
          <h4 className="font-medium mb-1">Analysis Result:</h4>
          <div className="whitespace-pre-line">{analysis.gpt_response.substring(0, 200)}...</div>
          <div className="mt-2 text-right">
            <button 
              className="text-green-600 hover:text-green-800 text-xs"
              onClick={() => {
                // Maybe open a modal or navigate to a page showing full analysis
                alert("Full analysis is available in the backend data/pre_market_result.json file");
              }}
            >
              View Full Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  )
}