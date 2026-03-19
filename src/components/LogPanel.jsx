import React, { useEffect, useRef } from 'react';
import { Terminal, Trash2 } from 'lucide-react';

const LogPanel = ({ logs, onClear }) => {
  const logEndRef = useRef(null);
  
  useEffect(() => {
    // 自动滚动到最新日志
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);
  
  const getLogColor = (level) => {
    switch (level) {
      case 'error':
        return '#ff6b6b';
      case 'warning':
        return '#ffa94d';
      case 'success':
        return '#51cf66';
      default:
        return '#4a90e2';
    }
  };
  
  const getLogIcon = (level) => {
    switch (level) {
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'success':
        return '✅';
      default:
        return 'ℹ️';
    }
  };
  
  return (
    <div style={{
      height: '200px',
      borderTop: '1px solid #e0e0e0',
      background: '#1e1e1e',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* 标题栏 */}
      <div style={{
        padding: '10px 15px',
        background: '#2d2d2d',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #3d3d3d'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Terminal size={16} />
          <span style={{ fontSize: '13px', fontWeight: '500' }}>日志面板</span>
          <span style={{
            fontSize: '11px',
            background: '#4a90e2',
            padding: '2px 8px',
            borderRadius: '10px'
          }}>
            {logs.length}
          </span>
        </div>
        <button
          onClick={onClear}
          style={{
            background: 'none',
            border: 'none',
            color: '#999',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            fontSize: '12px',
            padding: '5px 10px',
            borderRadius: '4px'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#3d3d3d';
            e.currentTarget.style.color = 'white';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'none';
            e.currentTarget.style.color = '#999';
          }}
        >
          <Trash2 size={14} />
          清空
        </button>
      </div>
      
      {/* 日志内容 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '10px',
        fontFamily: 'Consolas, Monaco, monospace',
        fontSize: '12px'
      }}>
        {logs.length === 0 ? (
          <div style={{
            color: '#666',
            textAlign: 'center',
            marginTop: '20px'
          }}>
            暂无日志
          </div>
        ) : (
          logs.map((log, index) => (
            <div
              key={index}
              style={{
                marginBottom: '5px',
                padding: '5px 8px',
                borderRadius: '4px',
                background: 'rgba(255,255,255,0.03)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px'
              }}
            >
              <span style={{ 
                color: '#888',
                fontSize: '11px',
                minWidth: '70px'
              }}>
                {log.time}
              </span>
              <span style={{ fontSize: '14px' }}>
                {getLogIcon(log.level)}
              </span>
              <span style={{ 
                color: getLogColor(log.level),
                flex: 1,
                wordBreak: 'break-word'
              }}>
                {log.message}
              </span>
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
};

export default LogPanel;
