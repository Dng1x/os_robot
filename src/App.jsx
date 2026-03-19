import React, { useState, useCallback, useRef, useEffect } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

import CustomNode from './components/CustomNode';
import AssetPanel from './components/AssetPanel';
import NodeToolbar from './components/NodeToolbar';
import PropertyPanel from './components/PropertyPanel';
import LogPanel from './components/LogPanel';
import ControlBar from './components/ControlBar';

import { NODE_TYPES_CONFIG } from './data/nodeTypes';
import { generateId, downloadFile, validateFlow, convertToBackendFormat, formatTime } from './utils/flowUtils';
import { flowAPI } from './utils/api';

const nodeTypes = {
  custom: CustomNode,
};

let id = 0;
const getId = () => `node_${id++}`;

function App() {
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [assets, setAssets] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentExecutingNode, setCurrentExecutingNode] = useState(null);

  // 添加日志
  const addLog = useCallback((message, level = 'info') => {
    const log = {
      time: formatTime(new Date()),
      message,
      level
    };
    setLogs(prev => [...prev, log]);
  }, []);

  // 拖拽创建节点
  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      if (!type) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const nodeConfig = NODE_TYPES_CONFIG.find(n => n.id === type);
      if (!nodeConfig) return;

      const newNode = {
        id: getId(),
        type: 'custom',
        position,
        data: {
          type: type,
          label: '',
          params: {}
        },
      };

      setNodes((nds) => nds.concat(newNode));
      addLog(`添加节点: ${nodeConfig.name}`, 'info');
    },
    [reactFlowInstance, addLog]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // 连接节点
  const onConnect = useCallback(
    (params) => {
      const sourceNode = nodes.find(n => n.id === params.source);
      const targetNode = nodes.find(n => n.id === params.target);
      
      let edgeType = 'default';
      if (params.sourceHandle === 'success' || params.sourceHandle === 'true') {
        edgeType = 'success';
      } else if (params.sourceHandle === 'failure' || params.sourceHandle === 'false') {
        edgeType = 'failure';
      } else if (params.sourceHandle === 'loop_body') {
        edgeType = 'loop';
      }

      const newEdge = {
        ...params,
        type: edgeType,
        animated: edgeType === 'loop',
        label: params.sourceHandle !== 'next' ? params.sourceHandle : undefined
      };

      setEdges((eds) => addEdge(newEdge, eds));
      addLog(`连接: ${sourceNode?.data.type} → ${targetNode?.data.type}`, 'info');
    },
    [nodes, addLog]
  );

  // 节点选择
  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  // 删除节点（按Delete或Backspace键）
  const onNodesDelete = useCallback((deleted) => {
    deleted.forEach(node => {
      addLog(`删除节点: ${node.data.type}`, 'warning');
    });
    if (selectedNode && deleted.find(n => n.id === selectedNode.id)) {
      setSelectedNode(null);
    }
  }, [selectedNode, addLog]);

  // 删除连接线
  const onEdgesDelete = useCallback((deleted) => {
    deleted.forEach(edge => {
      addLog(`删除连接线`, 'warning');
    });
  }, [addLog]);

  // 更新节点
  const onUpdateNode = useCallback((nodeId, newData) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              ...newData
            }
          };
        }
        return node;
      })
    );
  }, []);

  // 更新节点样式（用于高亮执行）
  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        style: {
          ...node.style,
          border: currentExecutingNode === node.id ? '3px solid #ffa94d' : undefined,
          boxShadow: currentExecutingNode === node.id ? '0 0 20px rgba(255, 169, 77, 0.5)' : undefined
        }
      }))
    );
  }, [currentExecutingNode]);

  // 素材管理
  const handleAddAsset = useCallback((asset) => {
    setAssets(prev => [...prev, asset]);
    addLog(`添加素材: ${asset.name}`, 'success');
  }, [addLog]);

  const handleDeleteAsset = useCallback((assetId) => {
    setAssets(prev => prev.filter(a => a.id !== assetId));
    addLog(`删除素材`, 'warning');
  }, [addLog]);

  const handleRenameAsset = useCallback((assetId, newName) => {
    setAssets(prev => prev.map(a => 
      a.id === assetId ? { ...a, name: newName } : a
    ));
    addLog(`重命名素材: ${newName}`, 'info');
  }, [addLog]);

  // 流程控制
  const handleRun = useCallback(async () => {
    const validation = validateFlow({ nodes, edges });
    if (!validation.valid) {
      alert(validation.error);
      addLog(`运行失败: ${validation.error}`, 'error');
      return;
    }

    setIsRunning(true);
    setCurrentExecutingNode(null);
    addLog('开始执行流程...', 'info');

    try {
      const flowData = convertToBackendFormat(nodes, edges, assets);
      const response = await flowAPI.execute(flowData);
      addLog('流程执行完成', 'success');
    } catch (error) {
      addLog(`执行出错: ${error.message}`, 'error');
    } finally {
      setIsRunning(false);
      setCurrentExecutingNode(null);
    }
  }, [nodes, edges, assets, addLog]);

  const handlePause = useCallback(() => {
    setIsRunning(false);
    addLog('暂停执行', 'warning');
  }, [addLog]);

  const handleStop = useCallback(async () => {
    try {
      await flowAPI.stop();
      setIsRunning(false);
      setCurrentExecutingNode(null);
      addLog('停止执行', 'warning');
    } catch (error) {
      addLog(`停止失败: ${error.message}`, 'error');
    }
  }, [addLog]);

  const handleStep = useCallback(() => {
    // 找到开始节点或下一个待执行节点
    if (!currentExecutingNode) {
      const startNode = nodes.find(n => n.data.type === 'start');
      if (startNode) {
        setCurrentExecutingNode(startNode.id);
        addLog(`单步执行: ${startNode.data.type}`, 'info');
      }
    } else {
      // 找到当前节点连接的下一个节点
      const nextEdge = edges.find(e => e.source === currentExecutingNode);
      if (nextEdge) {
        setCurrentExecutingNode(nextEdge.target);
        const nextNode = nodes.find(n => n.id === nextEdge.target);
        addLog(`单步执行: ${nextNode?.data.type}`, 'info');
      } else {
        addLog('已到达流程末尾', 'success');
        setCurrentExecutingNode(null);
      }
    }
  }, [currentExecutingNode, nodes, edges, addLog]);

  // 文件操作
  const handleSave = useCallback(() => {
    const flowData = convertToBackendFormat(nodes, edges, assets);
    const json = JSON.stringify(flowData, null, 2);
    downloadFile(json, 'flow.json');
    addLog('保存成功', 'success');
  }, [nodes, edges, assets, addLog]);

  const handleLoad = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const data = JSON.parse(event.target.result);
            // TODO: 转换并加载数据
            addLog('加载成功', 'success');
          } catch (err) {
            addLog('文件格式错误', 'error');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  }, [addLog]);

  const handleExportJSON = useCallback(() => {
    const flowData = convertToBackendFormat(nodes, edges, assets);
    const json = JSON.stringify(flowData, null, 2);
    downloadFile(json, `flow_${Date.now()}.json`);
    addLog('导出JSON成功', 'success');
  }, [nodes, edges, assets, addLog]);

  const handleImportJSON = useCallback((data) => {
    try {
      // 解析JSON数据
      if (!data || !data.nodes || !data.connections) {
        throw new Error('JSON格式不正确');
      }

      // 清空当前画布
      setNodes([]);
      setEdges([]);
      
      // 导入节点
      const importedNodes = data.nodes.map(node => ({
        id: node.id,
        type: 'custom',
        position: node.position || { x: 0, y: 0 },
        data: {
          type: node.data.type,
          label: node.data.label || '',
          params: node.data.params || {}
        }
      }));
      
      // 导入连接线
      const importedEdges = data.connections.map(conn => ({
        id: conn.id,
        source: conn.source,
        target: conn.target,
        sourceHandle: conn.sourceHandle,
        targetHandle: conn.targetHandle,
        type: conn.type || 'default'
      }));
      
      // 导入素材
      if (data.assets && data.assets.length > 0) {
        setAssets(data.assets);
        addLog(`导入 ${data.assets.length} 个素材`, 'info');
      }
      
      // 更新画布
      setNodes(importedNodes);
      setEdges(importedEdges);
      
      // 更新ID计数器
      const maxId = importedNodes.reduce((max, node) => {
        const nodeNum = parseInt(node.id.replace('node_', ''));
        return nodeNum > max ? nodeNum : max;
      }, 0);
      id = maxId + 1;
      
      addLog(`导入成功：${importedNodes.length} 个节点，${importedEdges.length} 条连接`, 'success');
    } catch (error) {
      console.error('导入失败:', error);
      addLog(`导入失败: ${error.message}`, 'error');
    }
  }, [addLog, setNodes, setEdges]);

  const handlePackageEXE = useCallback(async () => {
    addLog('开始打包EXE...', 'info');
    try {
      const flowData = convertToBackendFormat(nodes, edges, assets);
      const response = await flowAPI.packageEXE(flowData);
      addLog('打包成功', 'success');
    } catch (error) {
      addLog(`打包失败: ${error.message}`, 'error');
    }
  }, [nodes, edges, assets, addLog]);

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部控制栏 */}
      <ControlBar
        onRun={handleRun}
        onPause={handlePause}
        onStop={handleStop}
        onStep={handleStep}
        onSave={handleSave}
        onLoad={handleLoad}
        onExportJSON={handleExportJSON}
        onImportJSON={handleImportJSON}
        onPackageEXE={handlePackageEXE}
        isRunning={isRunning}
      />

      {/* 主工作区 */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* 左侧：素材库 */}
        <AssetPanel
          assets={assets}
          onAddAsset={handleAddAsset}
          onDeleteAsset={handleDeleteAsset}
          onRenameAsset={handleRenameAsset}
        />

        {/* 左侧：积木块工具栏 */}
        <NodeToolbar />

        {/* 中间：画布 */}
        <div ref={reactFlowWrapper} style={{ flex: 1, background: '#fafafa' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodeClick={onNodeClick}
            onNodesDelete={onNodesDelete}
            onEdgesDelete={onEdgesDelete}
            nodeTypes={nodeTypes}
            fitView
            snapToGrid
            snapGrid={[15, 15]}
            deleteKeyCode={['Backspace', 'Delete']}
          >
            <Background color="#e0e0e0" gap={15} />
            <Controls />
            <MiniMap
              nodeColor={(node) => {
                const nodeConfig = NODE_TYPES_CONFIG.find(n => n.id === node.data.type);
                return nodeConfig ? '#4a90e2' : '#999';
              }}
              maskColor="rgba(0, 0, 0, 0.1)"
            />
          </ReactFlow>
        </div>

        {/* 右侧：属性面板 */}
        <PropertyPanel
          selectedNode={selectedNode}
          assets={assets}
          onUpdateNode={onUpdateNode}
          onClose={() => setSelectedNode(null)}
        />
      </div>

      {/* 底部：日志面板 */}
      <LogPanel logs={logs} onClear={() => setLogs([])} />
    </div>
  );
}

function AppWithProvider() {
  return (
    <ReactFlowProvider>
      <App />
    </ReactFlowProvider>
  );
}

export default AppWithProvider;
