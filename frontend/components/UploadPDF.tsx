// /components/UploadPDF.tsx
import { useState } from 'react'

export default function UploadPDF() {
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const handleUpload = async () => {
    if (!file) {
      setStatus('Please select a file first')
      return
    }

    setIsUploading(true)
    setStatus('Uploading...')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch('http://localhost:8000/upload-pdf', {
        method: 'POST',
        body: formData,
      })

      const data = await res.json()
      setStatus(data.status || data.error || 'Upload successful')
    } catch (error) {
      setStatus('Upload failed. Please try again.')
      console.error(error)
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
          {isUploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      
      {status && (
        <div className={`mt-2 text-xs rounded-md p-2 ${
          status.includes('successful') 
            ? 'bg-green-50 text-green-700' 
            : status === 'Uploading...'
              ? 'bg-blue-50 text-blue-700'
              : 'bg-red-50 text-red-700'
        }`}>
          {status}
        </div>
      )}
    </div>
  )
}