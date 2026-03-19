import axios from 'axios';

const API_BASE_URL = '/api';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// 流程相关 API
export const flowAPI = {
  // 保存流程
  save: (flowData) => api.post('/flow/save', flowData),
  
  // 加载流程
  load: (flowId) => api.get(`/flow/load/${flowId}`),
  
  // 导出 JSON
  exportJSON: (flowData) => api.post('/flow/export', flowData),
  
  // 导入 JSON
  importJSON: (jsonData) => api.post('/flow/import', jsonData),
  
  // 打包 EXE
  packageEXE: (flowData) => api.post('/flow/package', flowData, {
    responseType: 'blob'
  }),
  
  // 执行流程
  execute: (flowData) => api.post('/flow/execute', flowData),
  
  // 单步执行
  stepExecute: (flowData, stepId) => api.post('/flow/step', { flowData, stepId }),
  
  // 停止执行
  stop: () => api.post('/flow/stop')
};

// 素材相关 API
export const assetAPI = {
  // 上传图片
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/asset/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  // 删除素材
  delete: (assetId) => api.delete(`/asset/${assetId}`),
  
  // 获取所有素材
  list: () => api.get('/asset/list')
};

// 日志相关 API
export const logAPI = {
  // 获取实时日志
  stream: () => {
    return new EventSource(`${API_BASE_URL}/log/stream`);
  },
  
  // 清空日志
  clear: () => api.post('/log/clear')
};

export default api;
