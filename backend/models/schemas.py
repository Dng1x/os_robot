"""
数据模型定义
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Asset(BaseModel):
    """素材模型"""
    id: str
    name: str
    path: str
    type: str


class NodeData(BaseModel):
    """节点数据模型"""
    type: str
    label: Optional[str] = ""
    params: Dict[str, Any] = Field(default_factory=dict)


class Node(BaseModel):
    """节点模型"""
    id: str
    type: str = "custom"
    position: Dict[str, float]
    data: NodeData


class Connection(BaseModel):
    """连接线模型"""
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None
    type: str = "default"


class FlowData(BaseModel):
    """流程数据模型"""
    name: str
    version: str = "1.0"
    assets: List[Asset] = Field(default_factory=list)
    nodes: List[Node] = Field(default_factory=list)
    connections: List[Connection] = Field(default_factory=list)


class FlowSaveResponse(BaseModel):
    """保存流程响应"""
    success: bool
    flow_id: str
    message: str


class FlowExecuteResponse(BaseModel):
    """执行流程响应"""
    success: bool
    message: str
    logs: List[dict] = Field(default_factory=list)


class LogEntry(BaseModel):
    """日志条目"""
    timestamp: str
    level: str
    message: str
