import React, { useState } from 'react';
import { Upload, Image, Trash2, FileImage, Edit2 } from 'lucide-react';

const AssetPanel = ({ assets, onAddAsset, onDeleteAsset, onRenameAsset }) => {
  const [isDragging, setIsDragging] = useState(false);
  
  const handleFileInput = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      for (let file of files) {
        await handleFile(file);
      }
    }
  };
  
  const handleFile = async (file) => {
    if (!file.type.startsWith('image/')) {
      alert('只支持图片文件');
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
      // 生成默认名称
      const assetCount = assets.length + 1;
      const defaultName = `素材${assetCount}`;
      
      // 弹窗让用户输入名称
      const assetName = prompt('请为素材命名：', defaultName);
      if (assetName === null) return; // 用户取消
      
      const asset = {
        id: `asset_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: assetName || defaultName,
        path: e.target.result,
        type: 'image',
        file: file
      };
      onAddAsset(asset);
    };
    reader.readAsDataURL(file);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      for (let file of files) {
        handleFile(file);
      }
    }
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
  };
  
  const handlePaste = async (e) => {
    const items = e.clipboardData.items;
    for (let item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        await handleFile(file);
      }
    }
  };
  
  return (
    <div 
      style={{
        width: '240px',
        height: '100%',
        borderRight: '1px solid #e0e0e0',
        background: '#f8f9fa',
        display: 'flex',
        flexDirection: 'column'
      }}
      onPaste={handlePaste}
      tabIndex={0}
    >
      {/* 标题 */}
      <div style={{
        padding: '15px',
        borderBottom: '1px solid #e0e0e0',
        fontWeight: 'bold',
        fontSize: '14px',
        background: 'white'
      }}>
        <FileImage size={16} style={{ display: 'inline', marginRight: '8px' }} />
        素材库
      </div>
      
      {/* 上传区域 */}
      <div
        style={{
          margin: '15px',
          padding: '20px',
          border: `2px dashed ${isDragging ? '#4a90e2' : '#d0d0d0'}`,
          borderRadius: '8px',
          textAlign: 'center',
          cursor: 'pointer',
          background: isDragging ? '#e3f2fd' : 'white',
          transition: 'all 0.3s'
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById('file-input').click()}
      >
        <Upload size={32} style={{ color: '#999', margin: '0 auto' }} />
        <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
          点击或拖拽上传图片
        </div>
        <div style={{ marginTop: '5px', fontSize: '11px', color: '#999' }}>
          支持 Ctrl+V 粘贴
        </div>
        <input
          id="file-input"
          type="file"
          accept="image/*"
          multiple
          style={{ display: 'none' }}
          onChange={handleFileInput}
        />
      </div>
      
      {/* 素材列表 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '0 15px'
      }}>
        {assets.length === 0 ? (
          <div style={{
            textAlign: 'center',
            color: '#999',
            fontSize: '12px',
            marginTop: '20px'
          }}>
            暂无素材
          </div>
        ) : (
          assets.map(asset => (
            <div
              key={asset.id}
              style={{
                background: 'white',
                borderRadius: '8px',
                padding: '10px',
                marginBottom: '10px',
                border: '1px solid #e0e0e0',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'}
              onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <img
                  src={asset.path}
                  alt={asset.name}
                  style={{
                    width: '50px',
                    height: '50px',
                    objectFit: 'cover',
                    borderRadius: '4px',
                    border: '1px solid #e0e0e0'
                  }}
                />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontSize: '13px',
                    fontWeight: '500',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {asset.name}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: '#999',
                    marginTop: '2px'
                  }}>
                    {asset.type}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    const newName = prompt('重命名素材：', asset.name);
                    if (newName && newName !== asset.name) {
                      onRenameAsset(asset.id, newName);
                    }
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#4a90e2',
                    padding: '5px',
                    marginRight: '5px'
                  }}
                  title="重命名"
                >
                  <Edit2 size={16} />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteAsset(asset.id);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#ff6b6b',
                    padding: '5px'
                  }}
                  title="删除"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AssetPanel;
