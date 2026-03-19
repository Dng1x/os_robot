import React, { useState } from 'react';
import { NODE_TYPES_CONFIG, NODE_CATEGORIES } from '../data/nodeTypes';
import { ChevronDown, ChevronRight, Box } from 'lucide-react';

const NodeToolbar = ({ onAddNode }) => {
  const [expandedCategories, setExpandedCategories] = useState(
    Object.keys(NODE_CATEGORIES).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {})
  );
  
  const toggleCategory = (categoryId) => {
    setExpandedCategories(prev => ({
      ...prev,
      [categoryId]: !prev[categoryId]
    }));
  };
  
  const handleDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };
  
  // 按类别分组节点
  const nodesByCategory = Object.keys(NODE_CATEGORIES).reduce((acc, key) => {
    acc[key] = NODE_TYPES_CONFIG.filter(node => node.category === key);
    return acc;
  }, {});
  
  return (
    <div style={{
      width: '240px',
      height: '100%',
      borderRight: '1px solid #e0e0e0',
      background: '#f8f9fa',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* 标题 */}
      <div style={{
        padding: '15px',
        borderBottom: '1px solid #e0e0e0',
        fontWeight: 'bold',
        fontSize: '14px',
        background: 'white'
      }}>
        <Box size={16} style={{ display: 'inline', marginRight: '8px' }} />
        积木块
      </div>
      
      {/* 节点列表 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '10px'
      }}>
        {Object.entries(NODE_CATEGORIES).map(([categoryId, category]) => (
          <div key={categoryId} style={{ marginBottom: '10px' }}>
            {/* 类别标题 */}
            <div
              onClick={() => toggleCategory(categoryId)}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '8px 10px',
                background: 'white',
                borderRadius: '6px',
                cursor: 'pointer',
                marginBottom: '5px',
                border: '1px solid #e0e0e0',
                fontWeight: '500',
                fontSize: '13px',
                color: category.color
              }}
            >
              {expandedCategories[categoryId] ? 
                <ChevronDown size={16} /> : 
                <ChevronRight size={16} />
              }
              <span style={{ marginLeft: '5px' }}>{category.name}</span>
              <span style={{
                marginLeft: 'auto',
                fontSize: '11px',
                background: category.color,
                color: 'white',
                padding: '2px 8px',
                borderRadius: '10px'
              }}>
                {nodesByCategory[categoryId].length}
              </span>
            </div>
            
            {/* 节点列表 */}
            {expandedCategories[categoryId] && (
              <div style={{ paddingLeft: '10px' }}>
                {nodesByCategory[categoryId].map(node => (
                  <div
                    key={node.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, node.id)}
                    style={{
                      padding: '8px 10px',
                      background: 'white',
                      borderRadius: '6px',
                      marginBottom: '5px',
                      cursor: 'grab',
                      border: '1px solid #e0e0e0',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateX(5px)';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                      e.currentTarget.style.borderColor = category.color;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateX(0)';
                      e.currentTarget.style.boxShadow = 'none';
                      e.currentTarget.style.borderColor = '#e0e0e0';
                    }}
                  >
                    <span style={{ fontSize: '16px' }}>{node.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ 
                        fontSize: '12px', 
                        fontWeight: '500',
                        color: '#333'
                      }}>
                        {node.name}
                      </div>
                      <div style={{ 
                        fontSize: '10px', 
                        color: '#999',
                        marginTop: '2px'
                      }}>
                        {node.description}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default NodeToolbar;
