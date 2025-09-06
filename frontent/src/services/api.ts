import axios from 'axios';
import { store } from '../store';
import { setGlobalError } from '../store/slices/uiSlice';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add bearer token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    try {
      const apiMessage = error?.response?.data?.detail || error?.response?.data?.message;
      if (apiMessage) {
        store.dispatch(setGlobalError(apiMessage));
      } else if (error?.message) {
        store.dispatch(setGlobalError(error.message));
      }
    } catch {}
    if (error.response?.status === 401) {
      // Token expired or invalid, clear storage and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', {
      email,
      password,
    });
    
    const { access_token, subscription_status } = response.data;
    
    // Store the access token
    localStorage.setItem('access_token', access_token);
    
    // Create user object from login response
    const user = {
      id: '1',
      email,
      name: email.split('@')[0],
      role: 'user' as const,
      isPro: subscription_status === 'active', // true if 'active', false otherwise
      createdAt: new Date().toISOString(),
    };
    
    return {
      user,
      token: access_token,
    };
  },

  register: async (email: string, password: string, name: string) => {
    // Mock implementation - replace with actual register endpoint when available
    const response = await api.post('/auth/register', { email, password, name });

    const { access_token } = response.data;

    // Store the access token
    localStorage.setItem('access_token', access_token);
    
    // Create user object from login response
    const user = {
      id: '1',
      email,
      name: email.split('@')[0],
      role: 'user' as const,
      isPro: false,
      createdAt: new Date().toISOString(),
    };
    
    return {
      user,
      token: access_token,
    };
  },

  requestPasswordReset: async (email: string) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },

  resetPassword: async (token: string, password: string) => {
    const response = await api.post('/auth/reset-password', { token, password });
    return response.data;
  },
};

export const appAPI = {
  getTasks: async () => {
    const response = await api.get('/tasks/my/');
    return response.data.map((task: any) => ({
      id: task.id.toString(),
      name: task.name,
      description: '',
      modelId: task.model_id.toString(),
      userId: task.user_id.toString(),
      status: 'completed' as const, // Default status since API doesn't provide it
      garmentType: 'top' as const, // Default garment type since API doesn't provide it
      createdAt: task.created_at || new Date().toISOString(),
      updatedAt: task.created_at || new Date().toISOString(),
      modelImages: task.model_images || [],
    }));
  },

  getModels: async () => {
    const response = await api.get('/models/');
    return response.data.map((model: any) => ({
      id: model.id.toString(),
      name: model.name || `Model ${model.id}`,
      description: model.description || '',
      tags: model.tags || [],
      images: model.images || [],
      thumbnail: model.images && model.images.length > 0 ? model.images[0] : '',
      userId: model.user_id?.toString() || '1',
      createdAt: model.created_at || new Date().toISOString(),
      isPublic: model.is_public || true,
    }));
  },

  createTask: async (taskData: { 
    name: string; 
    description?: string; 
    modelId: string; 
    pose?: string;
  }) => {
    const response = await api.post('/tasks/', {
      model_id: parseInt(taskData.modelId),
      name: taskData.name,
      Discription: taskData.description || '',
      pose: taskData.pose || 'standing',
    });
    
    return {
      id: response.data.id.toString(),
      name: response.data.name,
      description: response.data.Discription || '',
      modelId: response.data.model_id.toString(),
      userId: response.data.user_id?.toString() || '1',
      status: 'not_started' as const,
      garmentType: 'top' as const,
      createdAt: response.data.created_at || new Date().toISOString(),
      updatedAt: response.data.created_at || new Date().toISOString(),
      modelImages: response.data.model_images || [],
    };
  },

  uploadModel: async (modelData: { images: File[] }) => {
  const formData = new FormData();
  // Optional: include name if backend expects it in future, else omit
  // formData.append('name', modelData.name);

  modelData.images.forEach((image) => {
    if (!image) throw new Error("Invalid file");
    formData.append('files', image);
  });
  // Inspect FormData entries
  for (let pair of formData.entries()) {
    console.log(pair[0] + ':', pair[1]);
  }

  const response = await api.post('/models/', formData, {
    headers: {
        'Content-Type': 'multipart/form-data',
      },
  });

  const data = response.data;

  if (typeof data.model_id === 'undefined' || data.model_id === null) {
    throw new Error("API response did not return a valid 'model_id'.");
  }

  return {
    id: data.model_id ? data.model_id.toString() : '',
    name: data.name || '',
    description: data.description || '',
    tags: data.tags || [],
    images: Array.isArray(data.images) ? data.images : [],
    thumbnail: Array.isArray(data.images) && data.images.length > 0 ? data.images[0] : '',
    userId: data.user_id ? data.user_id.toString() : '1',
    createdAt: data.created_at || new Date().toISOString(),
    isPublic: typeof data.is_public === "boolean" ? data.is_public : true,
  };
},





  generateImages: async (taskId: string, garmentImages: File[]) => {
    const formData = new FormData();
    formData.append('task_id', taskId);
    
    garmentImages.forEach((image) => {
      formData.append('files', image);
    });

    const response = await api.post('/batches/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    // The API returns an array of batches, we'll return the latest one
    const batches = response.data;
    const latestBatch = batches[batches.length - 1];
    
    return {
      id: latestBatch.batch_id.toString(),
      taskId,
      batchNumber: latestBatch.batch_id,
      status: latestBatch.status === 'done' ? 'completed' : latestBatch.status,
      createdAt: latestBatch.created_at,
      garmentImages: latestBatch.garment_images.map((garment: any) => ({
        garmentImageId: garment.garment_image_id,
        imageUrl: garment.image_url,
        generatedImages: garment.generated_images.map((generated: any) => ({
          generatedImageId: generated.generated_image_id,
          outputUrl: generated.output_url,
          poseLabel: generated.pose_label,
          modelId: generated.model_id,
        })),
      })),
    };
  },

  getTaskBatches: async (taskId: string) => {
    const response = await api.get(`/tasks/${taskId}/batches/`);
    return response.data.map((batch: any) => ({
      id: batch.batch_id.toString(),
      taskId,
      batchNumber: batch.batch_id,
      status: batch.status === 'done' ? 'completed' : batch.status,
      createdAt: batch.created_at,
      garmentImages: batch.garment_images.map((garment: any) => ({
        garmentImageId: garment.garment_image_id,
        imageUrl: garment.image_url,
        generatedImages: garment.generated_images.map((generated: any) => ({
          generatedImageId: generated.generated_image_id,
          outputUrl: generated.output_url,
          poseLabel: generated.pose_label,
          modelId: generated.model_id,
        })),
      })),
    }));
  },
  // Placeholder: backend will provide this endpoint in future
  getRemainingImageTokens: async (): Promise<{ remaining: number }> => {
    try {
      const response = await api.get('/api/tokens/tokens/balance');
      const remaining =
        Number(response.data?.remaining || response.data?.token_balance || response.data?.quota_left) || 0;
      return { remaining };
    } catch (e) {
      return { remaining: 0 };
    }
  },
};

export const userAPI = {
  getProfile: async (): Promise<{ name: string; isPro: boolean; email?: string }> => {
    // Fetch basic profile
    const me = await api.get('/auth/me');
    const name = me.data?.name || me.data?.username || (me.data?.email ? String(me.data.email).split('@')[0] : 'User');
    const email = me.data?.email;
    let isPro = false;
    // Try to fetch subscription status if available
   
    
    const status = me.data?.status || me.data?.subscription_status;
    console.log('status:', status);
    isPro = status === 'active' ? true : false;

    return { name, isPro, email };
  },
};

export const paymentsAPI = {
  createPhonePeOrder: async (
    amountPaise: number,
    plan: number,
    currency: string = 'INR'
  ): Promise<{ tokenUrl: string; transactionId?: string }> => {
    const response = await api.post('/api/payments/create-phonepe-order', {
      amount: amountPaise,
      plan,
      currency,
    });
    console.log('createPhonePeOrder response:', response.data?.transactionId);
    // Normalize key just in case backend returns different casing
    const tokenUrl = response.data?.tokenUrl || response.data?.token_url;
    const transactionId =
      response.data?.transactionId ||
      response.data?.transaction_id ||
      response.data?.merchantTransactionId ||
      response.data?.merchant_transaction_id;
    return { tokenUrl, transactionId };
  },
  getPaymentStatus: async (
    transactionId: string
  ): Promise<{ status: string }> => {
    const response = await api.get(`/api/payments/phonepe-order-status/${transactionId}`);
    const status = response.data?.status || response.data?.payment_status;
    return { status };
  },
};

export default api;