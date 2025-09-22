import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000'
    : window.location.origin,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API请求:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API响应错误:', error.response?.status, error.response?.data);

    // 处理常见错误
    if (error.response?.status === 404) {
      console.error('API端点不存在');
    } else if (error.response?.status >= 500) {
      console.error('服务器内部错误');
    } else if (error.code === 'ECONNABORTED') {
      console.error('请求超时');
    } else if (!error.response) {
      console.error('网络连接错误');
    }

    return Promise.reject(error);
  }
);

// API方法
export const gameAPI = {
  // 健康检查
  healthCheck: () => api.get('/health'),

  // 房间管理
  getRooms: () => api.get('/api/rooms'),

  createRoom: (roomName = '默认房间') =>
    api.post('/api/rooms', null, { params: { room_name: roomName } }),

  // 获取房间信息
  getRoomInfo: (roomId) => api.get(`/api/rooms/${roomId}`),
};

// 工具函数
export const createWebSocketURL = (roomId, playerName) => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.hostname;
  const port = process.env.NODE_ENV === 'development' ? '8000' : window.location.port;

  return `${protocol}//${host}:${port}/ws/${roomId}/${encodeURIComponent(playerName)}`;
};

// 错误处理工具
export const handleAPIError = (error, defaultMessage = '操作失败') => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  } else if (error.response?.data?.message) {
    return error.response.data.message;
  } else if (error.message) {
    return error.message;
  } else {
    return defaultMessage;
  }
};

export default api;