import React from 'react';
import { MessageSquare, FileText, Activity } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header style={{
      background: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-color)',
      padding: '12px 24px',
      height: '65px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      {/* Brand Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '34px',
          height: '34px',
          borderRadius: '8px',
          background: 'var(--accent-blue)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff'
        }}>
          <MessageSquare size={18} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff' }}>Guidely</h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Internal Knowledge Assistant</p>
        </div>
      </div>

      {/* Tab Switcher */}
      <nav style={{ display: 'flex', gap: '6px', background: 'var(--bg-main)', padding: '3px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
        <button
          onClick={() => setActiveTab('chat')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 14px',
            borderRadius: '6px',
            fontSize: '0.85rem',
            fontWeight: 600,
            background: activeTab === 'chat' ? 'var(--bg-surface)' : 'transparent',
            color: activeTab === 'chat' ? '#ffffff' : 'var(--text-muted)',
            border: activeTab === 'chat' ? '1px solid var(--border-color)' : '1px solid transparent'
          }}
        >
          <MessageSquare size={14} />
          Chat Assistant
        </button>

        <button
          onClick={() => setActiveTab('admin')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 14px',
            borderRadius: '6px',
            fontSize: '0.85rem',
            fontWeight: 600,
            background: activeTab === 'admin' ? 'var(--bg-surface)' : 'transparent',
            color: activeTab === 'admin' ? '#ffffff' : 'var(--text-muted)',
            border: activeTab === 'admin' ? '1px solid var(--border-color)' : '1px solid transparent'
          }}
        >
          <FileText size={14} />
          Doc Management & Metrics
        </button>
      </nav>

      {/* Backend Status Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--success)', background: 'rgba(16, 185, 129, 0.1)', padding: '4px 10px', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
        <Activity size={12} />
        Backend Active
      </div>
    </header>
  );
}
