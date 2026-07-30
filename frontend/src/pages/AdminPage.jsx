import React, { useState, useEffect } from 'react';
import { Upload, RefreshCw, Database, Activity, Layers, FileCode, CheckCircle, AlertCircle, Clock, Zap } from 'lucide-react';

export default function AdminPage() {
  const [metrics, setMetrics] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  const fetchMetricsAndDocs = async () => {
    try {
      const [mRes, dRes] = await Promise.all([
        fetch('/metrics'),
        fetch('/api/documents')
      ]);

      if (mRes.ok) setMetrics(await mRes.json());
      if (dRes.ok) setDocuments(await dRes.json());
    } catch (err) {
      console.error("Failed to fetch admin metrics", err);
    }
  };

  useEffect(() => {
    fetchMetricsAndDocs();
  }, []);

  const handleReindex = async () => {
    setIndexing(true);
    setStatusMsg(null);
    try {
      const res = await fetch('/api/documents/index-all', { method: 'POST' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to reindex documents');
      
      setStatusMsg({ type: 'success', text: `${data.message} (${data.total_chunks} total chunks indexed)` });
      fetchMetricsAndDocs();
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message });
    } finally {
      setIndexing(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setStatusMsg(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');

      setStatusMsg({ type: 'success', text: `Uploaded ${data.filename} (${data.chunks_indexed} chunks indexed)` });
      fetchMetricsAndDocs();
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '24px auto', padding: '0 16px' }}>
      {/* Header Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: '#ffffff' }}>Document Management & Metrics</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Upload documents, trigger vector re-indexing, and monitor system latency.</p>
        </div>

        <button
          onClick={handleReindex}
          disabled={indexing}
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-color)',
            color: '#ffffff',
            padding: '8px 16px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <RefreshCw size={14} className={indexing ? "animate-spin" : ""} />
          {indexing ? "Indexing..." : "Trigger Re-Indexing"}
        </button>
      </div>

      {/* Status Alert */}
      {statusMsg && (
        <div style={{
          background: statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
          border: `1px solid ${statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          borderRadius: '8px',
          padding: '12px 16px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          color: statusMsg.type === 'success' ? '#34d399' : '#fca5a5',
          fontSize: '0.875rem'
        }}>
          {statusMsg.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          <span>{statusMsg.text}</span>
        </div>
      )}

      {/* Metrics Cards Grid */}
      {metrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px', marginBottom: '24px' }}>
          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '16px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
              <Database size={14} color="var(--accent-blue)" /> Documents
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ffffff' }}>{metrics.total_documents}</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '16px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
              <Layers size={14} color="#818cf8" /> Chunks
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ffffff' }}>{metrics.total_chunks}</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '16px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
              <Zap size={14} color="var(--success)" /> Cache Hit Rate
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ffffff' }}>{metrics.cache_hit_rate}%</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '16px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
              <Clock size={14} color="var(--warning)" /> Median Latency
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ffffff' }}>{metrics.median_latency_ms} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ms</span></div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '16px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
              <Activity size={14} color="#f43f5e" /> Latency (p95)
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ffffff' }}>{metrics.p95_latency_ms} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ms</span></div>
          </div>
        </div>
      )}

      {/* Upload Zone */}
      <div style={{ background: 'var(--bg-surface)', border: '1px dashed var(--border-color)', borderRadius: '10px', padding: '24px', textAlign: 'center', marginBottom: '24px' }}>
        <input
          type="file"
          id="fileUploadInput"
          accept=".txt,.md,.json,.csv"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
        />
        <label htmlFor="fileUploadInput" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
          <Upload size={22} color="var(--accent-blue)" />
          <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#ffffff' }}>
            {uploading ? "Uploading & Indexing..." : "Click to Upload Document"}
          </span>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            Supports plain text (.txt), Markdown (.md), JSON docs.
          </span>
        </label>
      </div>

      {/* Document Table */}
      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '16px' }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff', marginBottom: '12px' }}>Indexed Documents</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '8px 12px' }}>Filename</th>
              <th style={{ padding: '8px 12px' }}>Chunks</th>
              <th style={{ padding: '8px 12px' }}>Size</th>
              <th style={{ padding: '8px 12px' }}>Last Modified</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                <td style={{ padding: '10px 12px', fontWeight: 600, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FileCode size={14} color="var(--accent-blue)" /> {doc.filename}
                </td>
                <td style={{ padding: '10px 12px' }}><span className="tag">{doc.chunk_count} Chunks</span></td>
                <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>{(doc.file_size_bytes / 1024).toFixed(1)} KB</td>
                <td style={{ padding: '10px 12px', color: 'var(--text-dim)' }}>{new Date(doc.last_modified * 1000).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
