import React, { useState, useEffect } from 'react';
import { Settings, X } from 'lucide-react';
import { NODE_TYPES_CONFIG } from '../data/nodeTypes';

const PropertyPanel = ({ selectedNode, assets, onUpdateNode, onClose }) => {
  const [formData, setFormData] = useState({});
  
  useEffect(() => {
    if (selectedNode) {
      setFormData(selectedNode.data.params || {});
    }
  }, [selectedNode]);
  
  if (!selectedNode) {
    return (
      <div style={{
        width: '300px',
        height: '100%',
        borderLeft: '1px solid #e0e0e0',
        background: '#f8f9fa',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#999',
        fontSize: '14px'
      }}>
        选择一个节点进行配置
      </div>
    );
  }
  
  const nodeConfig = NODE_TYPES_CONFIG.find(n => n.id === selectedNode.data.type);
  
  if (!nodeConfig) {
    return <div>未知节点类型</div>;
  }
  
  const handleChange = (paramName, value) => {
    const newFormData = { ...formData, [paramName]: value };
    setFormData(newFormData);
    onUpdateNode(selectedNode.id, { params: newFormData });
  };
  
  const renderInput = (param) => {
    const value = formData[param.name] ?? param.default ?? '';
    
    // 条件显示逻辑
    const shouldShow = () => {
      // 点击/双击节点：根据位置类型显示不同字段
      if (param.name === 'position_var' || param.name === 'offset_x' || param.name === 'offset_y') {
        return formData['position_type'] === '使用变量';
      }
      if (param.name === 'fixed_x' || param.name === 'fixed_y') {
        return formData['position_type'] === '固定坐标';
      }
      
      // 拖拽节点
      if (param.name === 'from_var') {
        return formData['from_type'] === '使用变量';
      }
      if (param.name === 'from_x' || param.name === 'from_y') {
        return formData['from_type'] === '固定坐标';
      }
      if (param.name === 'to_var') {
        return formData['to_type'] === '使用变量';
      }
      if (param.name === 'to_x' || param.name === 'to_y') {
        return formData['to_type'] === '固定坐标' || formData['to_type'] === '相对偏移';
      }
      
      // 变量节点
      if (param.name === 'source_output') {
        return formData['mode'] === '设置变量' && formData['source_type'] === '前一个节点输出';
      }
      if (param.name === 'direct_value') {
        return formData['mode'] === '设置变量' && formData['source_type'] === '直接输入';
      }
      if (param.name === 'expression' || param.name === 'source_type') {
        return formData['mode'] === '设置变量';
      }
      
      return true;
    };
    
    if (!shouldShow()) {
      return null;
    }
    
    switch (param.type) {
      case 'text':
      case 'file':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleChange(param.name, e.target.value)}
            placeholder={param.placeholder || param.help || `请输入${param.label}`}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              fontSize: '13px'
            }}
          />
        );
      
      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => handleChange(param.name, e.target.value)}
            placeholder={param.placeholder || param.help || `请输入${param.label}`}
            rows={3}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              fontSize: '13px',
              resize: 'vertical',
              fontFamily: 'monospace'
            }}
          />
        );
      
      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleChange(param.name, parseFloat(e.target.value))}
            min={param.min}
            max={param.max}
            step={param.step || 1}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              fontSize: '13px'
            }}
          />
        );
      
      case 'slider':
        return (
          <div>
            <input
              type="range"
              value={value}
              onChange={(e) => handleChange(param.name, parseFloat(e.target.value))}
              min={param.min || 0}
              max={param.max || 1}
              step={param.step || 0.01}
              style={{ width: '100%' }}
            />
            <div style={{ 
              textAlign: 'center', 
              fontSize: '12px', 
              color: '#666',
              marginTop: '5px'
            }}>
              {value}
            </div>
          </div>
        );
      
      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleChange(param.name, e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              fontSize: '13px'
            }}
          >
            {param.options.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        );
      
      case 'image':
        return (
          <select
            value={value}
            onChange={(e) => {
              const selectedAsset = assets.find(a => a.id === e.target.value);
              handleChange(param.name, selectedAsset ? selectedAsset.name : e.target.value);
            }}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              fontSize: '13px'
            }}
          >
            <option value="">请选择图片</option>
            {assets.filter(a => a.type === 'image').map(asset => (
              <option key={asset.id} value={asset.id}>{asset.name}</option>
            ))}
          </select>
        );
      
      case 'color':
        return (
          <input
            type="color"
            value={value}
            onChange={(e) => handleChange(param.name, e.target.value)}
            style={{
              width: '100%',
              height: '40px',
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          />
        );
      
      case 'position':
      case 'region':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleChange(param.name, e.target.value)}
            placeholder={param.help || "格式: x,y 或 x,y,width,height"}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              fontSize: '13px'
            }}
          />
        );
      
      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleChange(param.name, e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              fontSize: '13px'
            }}
          />
        );
    }
  };
  
  return (
    <div style={{
      width: '300px',
      height: '100%',
      borderLeft: '1px solid #e0e0e0',
      background: '#f8f9fa',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* 标题 */}
      <div style={{
        padding: '15px',
        borderBottom: '1px solid #e0e0e0',
        background: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Settings size={16} />
          <span style={{ fontWeight: 'bold', fontSize: '14px' }}>属性配置</span>
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#666',
            padding: '5px'
          }}
        >
          <X size={16} />
        </button>
      </div>
      
      {/* 节点信息 */}
      <div style={{
        padding: '15px',
        background: 'white',
        borderBottom: '1px solid #e0e0e0'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '10px',
          marginBottom: '10px'
        }}>
          <span style={{ fontSize: '24px' }}>{nodeConfig.icon}</span>
          <div>
            <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
              {nodeConfig.name}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              {nodeConfig.description}
            </div>
          </div>
        </div>
      </div>
      
      {/* 参数配置 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '15px'
      }}>
        {nodeConfig.params && nodeConfig.params.length > 0 ? (
          <>
            {nodeConfig.params.map(param => (
              <div key={param.name} style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '500',
                  marginBottom: '8px',
                  color: '#333'
                }}>
                  {param.label}
                  {param.required && <span style={{ color: '#ff6b6b' }}> *</span>}
                </label>
                {renderInput(param)}
                {param.help && (
                  <div style={{
                    fontSize: '11px',
                    color: '#999',
                    marginTop: '5px'
                  }}>
                    {param.help}
                  </div>
                )}
              </div>
            ))}
            
            {/* 通用参数：最大经过次数（除了开始和结束节点） */}
            {selectedNode.data.type !== 'start' && selectedNode.data.type !== 'end' && (
              <div style={{ 
                marginBottom: '20px',
                paddingTop: '15px',
                borderTop: '1px dashed #e0e0e0'
              }}>
                <label style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '500',
                  marginBottom: '8px',
                  color: '#333'
                }}>
                  最大经过次数
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.max_passes ?? 999999}
                  onChange={(e) => handleChange('max_passes', parseInt(e.target.value) || 999999)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #d0d0d0',
                    borderRadius: '5px',
                    fontSize: '13px',
                    boxSizing: 'border-box'
                  }}
                />
                <div style={{
                  fontSize: '11px',
                  color: '#999',
                  marginTop: '5px'
                }}>
                  节点最多可经过几次，超过后终止流程（默认999999次≈无限）
                </div>
              </div>
            )}
            
            {/* 输出变量提示 */}
            {nodeConfig.variables && nodeConfig.variables.length > 0 && (
              <div style={{
                marginTop: '20px',
                padding: '12px',
                background: '#e3f2fd',
                borderRadius: '6px',
                borderLeft: '3px solid #2196f3'
              }}>
                <div style={{
                  fontSize: '12px',
                  fontWeight: 'bold',
                  color: '#1976d2',
                  marginBottom: '8px'
                }}>
                  📤 输出变量
                </div>
                {nodeConfig.variables.map((variable, index) => (
                  <div key={index} style={{
                    fontSize: '11px',
                    color: '#555',
                    marginBottom: '4px',
                    paddingLeft: '8px'
                  }}>
                    <code style={{
                      background: '#fff',
                      padding: '2px 6px',
                      borderRadius: '3px',
                      color: '#d32f2f',
                      fontWeight: 'bold'
                    }}>
                      {variable.name}
                    </code>
                    <span style={{ color: '#666', fontSize: '10px', marginLeft: '6px' }}>
                      ({variable.type})
                    </span>
                    {variable.description && (
                      <span style={{ marginLeft: '8px', color: '#777' }}>
                        {variable.description}
                      </span>
                    )}
                  </div>
                ))}
                {nodeConfig.outputHint && (
                  <div style={{
                    marginTop: '8px',
                    paddingTop: '8px',
                    borderTop: '1px solid #bbdefb',
                    fontSize: '11px',
                    color: '#666',
                    whiteSpace: 'pre-line'
                  }}>
                    💡 {nodeConfig.outputHint}
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <div style={{
            textAlign: 'center',
            color: '#999',
            fontSize: '12px',
            marginTop: '20px'
          }}>
            该节点无需配置参数
          </div>
        )}
      </div>
    </div>
  );
};

export default PropertyPanel;
