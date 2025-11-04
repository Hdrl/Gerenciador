// 📁 src/axiosConfig.js (ou onde você o salvou)

import axios from "axios";

const baseURL = 'http://127.0.0.1:8000'

const apiClient = axios.create({
    baseURL: baseURL,
    timeout: 5000,
    headers:{
        'Content-Type': 'application/json'
    }
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken'); 
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        console.error("Erro 401: Não autorizado. Deslogando...");
      }
      return Promise.reject(error.response.data);
    } else if (error.request) {
      return Promise.reject({ general: 'API offline ou indisponível.' });
    } else {
      return Promise.reject({ general: 'Erro inesperado na configuração.' });
    }
  }
);


export default apiClient;