import React, { useState } from 'react';
import { 
  Play, Pause, Square, SkipForward, 
  Save, FolderOpen, Download, Upload,
  Package, FileJson
} from 'lucide-react';

const ControlBar = ({ 
  onRun, 
  onPause, 
  onStop, 
  onStep,
  onSave,
  onLoad,
  onExportJSON,
  onImportJSON,
  onPackageEXE,
  isRunning
}) => {
  const [showMenu, setShowMenu] = useState(null);
  
  const buttonStyle = {
    padding: '8px 16px',
    background: 'white',
    border: '1px solid #d0d0d0',
    borderRadius: '6px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '13px',
    fontWeight: '500',
    transition: 'all 0.2s'
  };
  
  const disabledButtonStyle = {
    ...buttonStyle,
    opacity: 0.5,
    cursor: 'not-allowed'
  };
  
  const primaryButtonStyle = {
    ...buttonStyle,
    background: '#4a90e2',
    color: 'white',
    border: 'none'
  };
  
  const dangerButtonStyle = {
    ...buttonStyle,
    background: '#ff6b6b',
    color: 'white',
    border: 'none'
  };
  
  const handleFileImport = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const data = JSON.parse(event.target.result);
          onImportJSON(data);
        } catch (err) {
          alert('JSON文件格式错误');
        }
      };
      reader.readAsText(file);
    }
  };
  
  return (
    <div style={{
      height: '60px',
      borderBottom: '1px solid #e0e0e0',
      background: '#f8f9fa',
      padding: '0 20px',
      display: 'flex',
      alignItems: 'center',
      gap: '10px'
    }}>
      {/* 左侧：文件操作 */}
      <div style={{ display: 'flex', gap: '10px', marginRight: 'auto' }}>
        <button
          style={buttonStyle}
          onClick={onSave}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#f0f0f0';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'white';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <Save size={16} />
          保存
        </button>
        
        <button
          style={buttonStyle}
          onClick={onLoad}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#f0f0f0';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'white';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <FolderOpen size={16} />
          打开
        </button>
        
        <div style={{ width: '1px', background: '#d0d0d0', height: '30px' }} />
        
        <button
          style={buttonStyle}
          onClick={onExportJSON}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#f0f0f0';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'white';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <Download size={16} />
          导出JSON
        </button>
        
        <label style={buttonStyle}>
          <Upload size={16} />
          导入JSON
          <input
            type="file"
            accept=".json"
            style={{ display: 'none' }}
            onChange={handleFileImport}
          />
        </label>
        
        <button
          style={buttonStyle}
          onClick={onPackageEXE}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#f0f0f0';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'white';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <Package size={16} />
          打包EXE
        </button>
      </div>
      
      {/* 右侧：执行控制 */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          style={!isRunning ? primaryButtonStyle : disabledButtonStyle}
          onClick={onRun}
          disabled={isRunning}
          onMouseEnter={(e) => {
            if (!isRunning) {
              e.currentTarget.style.background = '#357abd';
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(74,144,226,0.3)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isRunning) {
              e.currentTarget.style.background = '#4a90e2';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }
          }}
        >
          <Play size={16} />
          运行
        </button>
        
        <button
          style={isRunning ? buttonStyle : disabledButtonStyle}
          onClick={onPause}
          disabled={!isRunning}
          onMouseEnter={(e) => {
            if (isRunning) {
              e.currentTarget.style.background = '#f0f0f0';
              e.currentTarget.style.transform = 'translateY(-1px)';
            }
          }}
          onMouseLeave={(e) => {
            if (isRunning) {
              e.currentTarget.style.background = 'white';
              e.currentTarget.style.transform = 'translateY(0)';
            }
          }}
        >
          <Pause size={16} />
          暂停
        </button>
        
        <button
          style={isRunning ? dangerButtonStyle : disabledButtonStyle}
          onClick={onStop}
          disabled={!isRunning}
          onMouseEnter={(e) => {
            if (isRunning) {
              e.currentTarget.style.background = '#e63946';
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(255,107,107,0.3)';
            }
          }}
          onMouseLeave={(e) => {
            if (isRunning) {
              e.currentTarget.style.background = '#ff6b6b';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }
          }}
        >
          <Square size={16} />
          停止
        </button>
        
        <button
          style={isRunning ? disabledButtonStyle : buttonStyle}
          onClick={onStep}
          disabled={isRunning}
          onMouseEnter={(e) => {
            if (!isRunning) {
              e.currentTarget.style.background = '#f0f0f0';
              e.currentTarget.style.transform = 'translateY(-1px)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isRunning) {
              e.currentTarget.style.background = 'white';
              e.currentTarget.style.transform = 'translateY(0)';
            }
          }}
        >
          <SkipForward size={16} />
          单步
        </button>
      </div>
    </div>
  );
};

export default ControlBar;
