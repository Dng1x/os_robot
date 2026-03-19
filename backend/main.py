"""
自动化工具后端 - FastAPI 主程序
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from typing import Optional
import json
import os
import asyncio
from datetime import datetime

from models import FlowData, FlowSaveResponse, FlowExecuteResponse
from executor import FlowExecutor
from utils.logger import log_manager, log_queue

# 创建 FastAPI 应用
app = FastAPI(
    title="自动化脚本工具 API",
    description="自动化脚本设计工具后端服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储目录
STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'storage')
FLOWS_DIR = os.path.join(STORAGE_DIR, 'flows')
ASSETS_DIR = os.path.join(STORAGE_DIR, 'assets')

# 确保目录存在
os.makedirs(FLOWS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# 全局执行器
current_executor: Optional[FlowExecutor] = None


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "自动化脚本工具 API",
        "version": "1.0.0",
        "status": "running"
    }


# ========== 流程管理接口 ==========

@app.post("/api/flow/save")
async def save_flow(flow_data: FlowData) -> FlowSaveResponse:
    """保存流程"""
    try:
        # 生成流程ID
        flow_id = f"flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 保存到文件
        file_path = os.path.join(FLOWS_DIR, f"{flow_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(flow_data.dict(), f, ensure_ascii=False, indent=2)
        
        return FlowSaveResponse(
            success=True,
            flow_id=flow_id,
            message="保存成功"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@app.get("/api/flow/load/{flow_id}")
async def load_flow(flow_id: str):
    """加载流程"""
    try:
        file_path = os.path.join(FLOWS_DIR, f"{flow_id}.json")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="流程不存在")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
        
        return flow_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载失败: {str(e)}")


@app.post("/api/flow/export")
async def export_flow(flow_data: FlowData):
    """导出流程为 JSON 文件"""
    try:
        # 转换为 JSON
        json_content = json.dumps(flow_data.dict(), ensure_ascii=False, indent=2)
        
        # 返回文件
        from io import BytesIO
        buffer = BytesIO(json_content.encode('utf-8'))
        
        return StreamingResponse(
            buffer,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={flow_data.name}.json"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@app.post("/api/flow/import")
async def import_flow(file: UploadFile = File(...)):
    """导入流程 JSON"""
    try:
        # 读取文件
        content = await file.read()
        flow_data = json.loads(content.decode('utf-8'))
        
        # 验证数据
        FlowData(**flow_data)
        
        return {
            "success": True,
            "message": "导入成功",
            "data": flow_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"导入失败: {str(e)}")


@app.post("/api/flow/execute")
async def execute_flow(flow_data: FlowData) -> FlowExecuteResponse:
    """执行流程"""
    global current_executor
    
    try:
        # 创建执行器
        current_executor = FlowExecutor(flow_data.dict())
        
        # 在后台线程执行（避免阻塞）
        import threading
        
        result = {'success': True, 'message': '执行完成', 'logs': []}
        
        def run_executor():
            nonlocal result
            result = current_executor.execute()
        
        thread = threading.Thread(target=run_executor)
        thread.start()
        thread.join(timeout=300)  # 最长5分钟
        
        if thread.is_alive():
            current_executor.stop()
            result = {
                'success': False,
                'message': '执行超时',
                'logs': log_manager.get_logs()
            }
        
        return FlowExecuteResponse(**result)
    
    except Exception as e:
        log_manager.log(f"执行异常: {str(e)}", 'error')
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")


@app.post("/api/flow/step")
async def step_flow():
    """单步执行（暂未实现完整功能）"""
    return {
        "success": True,
        "message": "单步执行功能开发中"
    }


@app.post("/api/flow/stop")
async def stop_flow():
    """停止执行"""
    global current_executor
    
    if current_executor:
        current_executor.stop()
        return {
            "success": True,
            "message": "已停止执行"
        }
    else:
        return {
            "success": False,
            "message": "没有正在执行的流程"
        }


@app.post("/api/flow/package")
async def package_flow(flow_data: FlowData):
    """打包为 EXE（暂未实现）"""
    return {
        "success": False,
        "message": "打包功能开发中，请使用 PyInstaller 手动打包"
    }


# ========== 素材管理接口 ==========

@app.post("/api/asset/upload")
async def upload_asset(file: UploadFile = File(...)):
    """上传素材"""
    try:
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"asset_{timestamp}_{file.filename}"
        file_path = os.path.join(ASSETS_DIR, filename)
        
        # 保存文件
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return {
            "success": True,
            "asset_id": filename,
            "path": file_path,
            "message": "上传成功"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@app.delete("/api/asset/{asset_id}")
async def delete_asset(asset_id: str):
    """删除素材"""
    try:
        file_path = os.path.join(ASSETS_DIR, asset_id)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return {
                "success": True,
                "message": "删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail="素材不存在")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@app.get("/api/asset/list")
async def list_assets():
    """获取素材列表"""
    try:
        assets = []
        for filename in os.listdir(ASSETS_DIR):
            file_path = os.path.join(ASSETS_DIR, filename)
            if os.path.isfile(file_path):
                assets.append({
                    "id": filename,
                    "name": filename,
                    "path": file_path
                })
        
        return {
            "success": True,
            "assets": assets
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}")


# ========== 日志接口 ==========

@app.get("/api/log/stream")
async def stream_logs():
    """实时日志流（SSE）"""
    async def event_generator():
        while True:
            # 从队列获取日志
            if not log_queue.empty():
                log_entry = log_queue.get()
                yield f"data: {json.dumps(log_entry)}\n\n"
            await asyncio.sleep(0.1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.post("/api/log/clear")
async def clear_logs():
    """清空日志"""
    log_manager.clear_logs()
    return {
        "success": True,
        "message": "日志已清空"
    }


# ========== 启动服务器 ==========

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("自动化脚本工具后端服务")
    print("=" * 60)
    print("API 文档: http://localhost:8000/docs")
    print("前端地址: http://localhost:5173")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
