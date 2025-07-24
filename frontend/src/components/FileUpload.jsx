import { useState, useEffect } from 'react';
import './FileUpload.css';

const FileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // Fetch uploaded files on load
  useEffect(() => {
    fetchUploadedFiles();
  }, []);

  useEffect(() => {
  if (messages.length > 0) {
    const timer = setTimeout(() => {
      setMessages([]);  // Clear all messages after 5 seconds
    }, 5000);
    return () => clearTimeout(timer); // Cleanup on unmount or before next effect
  }
}, [messages]);

  const fetchUploadedFiles = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/uploaded-files/");
      const data = await res.json();

      if (res.ok) {
        setUploadedFiles(data);
      } else {
        console.error("Failed to fetch files:", data);
      }
    } catch (err) {
      console.error("Error fetching uploaded files:", err);
    }
  };

  const handleChange = async (e) => {
    const files = Array.from(e.target.files);
    setMessages([]);
    
    const validFiles = files.filter(file => file.type === "application/pdf");

    if (validFiles.length === 0) {
      alert("Please upload one or more valid PDF files.");
      return;
    }

    const formData = new FormData();
    validFiles.forEach(file => {
      formData.append("files", file);
    });

    setUploading(true);
    try {
      const response = await fetch("http://localhost:8000/api/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.error || "Upload failed");
      }

      const results = data.results || [];
      const statusMessages = results.map(res => {
        if (res.status === "success") {
          return `${res.filename} uploaded successfully!!`;
        } else if (res.status === "error") {
          return `${res.filename} failed: ${res.error}`;
        } else if (res.status === "invalid") {
          return `${res.filename} is invalid: ${JSON.stringify(res.errors)}`;
        }
        return `${res.filename}: Unknown response.`;
      });

      setMessages(statusMessages);
      await fetchUploadedFiles();
    } catch (err) {
      console.error("Upload error:", err);
      setMessages([`${err.message}`]);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <label htmlFor="upload" className={`upload-label ${uploading ? 'disabled' : ''}`}>
        {uploading ? 'Uploading...' : 'Upload PDFs'}
      </label>
      <input
        id="upload"
        type="file"
        accept="application/pdf"
        multiple
        onChange={handleChange}
        disabled={uploading}
      />
      {messages.length > 0 && (
        <div className="upload-messages">
          {messages.map((msg, idx) => (
            <p key={idx} className="upload-message">{msg}</p>
          ))}
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h2>Files</h2>
          <ul>
            {uploadedFiles.map(file => (
              <li key={file.id}>
                {file.file}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
