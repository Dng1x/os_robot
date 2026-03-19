// 生成唯一 ID
export const generateId = () => {
  return `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// 下载文件
export const downloadFile = (content, filename, type = 'application/json') => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// 读取文件
export const readFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = (e) => reject(e);
    reader.readAsText(file);
  });
};

// 验证流程数据
export const validateFlow = (flowData) => {
  if (!flowData.nodes || !Array.isArray(flowData.nodes)) {
    return { valid: false, error: '缺少节点数据' };
  }
  
  if (!flowData.edges || !Array.isArray(flowData.edges)) {
    return { valid: false, error: '缺少连接线数据' };
  }
  
  // 检查是否有开始节点 - 修复：检查 data.type 而不是 type
  const hasStart = flowData.nodes.some(node => node.data && node.data.type === 'start');
  if (!hasStart) {
    return { valid: false, error: '流程必须有一个开始节点' };
  }
  
  return { valid: true };
};

// 转换为后端格式
export const convertToBackendFormat = (nodes, edges, assets) => {
  return {
    name: '未命名流程',
    version: '1.0',
    assets: assets.map(asset => ({
      id: asset.id,
      name: asset.name,
      path: asset.path,
      type: asset.type
    })),
    nodes: nodes.map(node => ({
      id: node.id,
      type: node.type,
      position: node.position,
      data: node.data
    })),
    connections: edges.map(edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      sourceHandle: edge.sourceHandle,
      targetHandle: edge.targetHandle,
      type: edge.type,
      label: edge.label
    }))
  };
};

// 从后端格式转换
export const convertFromBackendFormat = (backendData) => {
  const nodes = backendData.nodes.map(node => ({
    id: node.id,
    type: node.type,
    position: node.position,
    data: node.data
  }));
  
  const edges = backendData.connections.map(conn => ({
    id: conn.id,
    source: conn.source,
    target: conn.target,
    sourceHandle: conn.sourceHandle,
    targetHandle: conn.targetHandle,
    type: conn.type || 'default',
    label: conn.label,
    animated: conn.type === 'loop'
  }));
  
  const assets = backendData.assets || [];
  
  return { nodes, edges, assets };
};

// 格式化时间
export const formatTime = (date) => {
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

// 深拷贝
export const deepClone = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};
