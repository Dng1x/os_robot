import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { NODE_TYPES_CONFIG, NODE_CATEGORIES } from '../data/nodeTypes';

const CustomNode = ({ data, selected }) => {
  const nodeConfig = NODE_TYPES_CONFIG.find(n => n.id === data.type);
  const category = NODE_CATEGORIES[nodeConfig?.category];
  
  if (!nodeConfig) {
    return <div>未知节点类型</div>;
  }
  
  const hasInputHandle = nodeConfig.id !== 'start';
  const hasOutputHandles = nodeConfig.outputs && nodeConfig.outputs.length > 0;
  
  // 获取节点的额外显示信息
  const getDisplayLabel = () => {
    if (data.label) return data.label;
    
    // 如果是找图节点且选择了图片，显示素材名
    if (data.type === 'find_image' && data.params?.image) {
      return `图片: ${data.params.image}`;
    }
    
    return '';
  };
  
  const displayLabel = getDisplayLabel();
  
  return (
    <div 
      style={{
        padding: '10px 15px',
        borderRadius: '8px',
        border: `2px solid ${selected ? '#ff6b6b' : category?.color || '#4a90e2'}`,
        background: 'white',
        minWidth: '120px',
        boxShadow: selected ? '0 4px 12px rgba(255,107,107,0.3)' : '0 2px 8px rgba(0,0,0,0.1)'
      }}
    >
      {/* 输入连接点 */}
      {hasInputHandle && (
        <Handle
          type="target"
          position={Position.Top}
          style={{
            background: category?.color || '#4a90e2',
            width: '10px',
            height: '10px',
            border: '2px solid white'
          }}
        />
      )}
      
      {/* 节点内容 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '18px' }}>{nodeConfig.icon}</span>
        <div style={{ flex: 1 }}>
          <div style={{ 
            fontWeight: 'bold', 
            fontSize: '13px',
            color: '#333'
          }}>
            {nodeConfig.name}
          </div>
          {displayLabel && (
            <div style={{ 
              fontSize: '11px', 
              color: '#666',
              marginTop: '2px',
              maxWidth: '150px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              {displayLabel}
            </div>
          )}
        </div>
      </div>
      
      {/* 输出连接点 */}
      {hasOutputHandles && (
        <>
          {nodeConfig.outputs.map((output, index) => {
            let position = Position.Bottom;
            let style = {
              background: category?.color || '#4a90e2',
              width: '10px',
              height: '10px',
              border: '2px solid white'
            };
            
            // 根据输出类型设置位置和颜色
            if (nodeConfig.outputs.length === 1) {
              // 单个输出：底部中间
              position = Position.Bottom;
            } else if (nodeConfig.outputs.length === 2) {
              // 两个输出：左右分布（用于条件分支）
              position = index === 0 ? Position.Right : Position.Left;
              if (output === 'true' || output === 'success') {
                style.background = '#51cf66';
              } else if (output === 'false' || output === 'failure') {
                style.background = '#ff6b6b';
              }
            } else {
              // 多个输出：底部分布
              position = Position.Bottom;
              style.left = `${(100 / (nodeConfig.outputs.length + 1)) * (index + 1)}%`;
            }
            
            return (
              <Handle
                key={output}
                type="source"
                position={position}
                id={output}
                style={style}
              />
            );
          })}
        </>
      )}
    </div>
  );
};

export default memo(CustomNode);
