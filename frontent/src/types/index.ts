export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
  avatar?: string;
  isPro: boolean;
  createdAt: string;
}

export interface AIModel {
  id: string;
  name: string;
  description: string;
  tags: string[];
  images: string[];
  thumbnail: string;
  userId: string;
  createdAt: string;
  isPublic: boolean;
}

export interface Task {
  id: string;
  name: string;
  description?: string;
  modelId: string;
  userId: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'failed';
  garmentType: 'top' | 'bottom' | 'onepiece';
  createdAt: string;
  updatedAt: string;
  modelImages?: string[];
  pose?: string;
}

export interface GenerationBatch {
  id: string;
  taskId: string;
  batchNumber: number;
  status: 'pending' | 'generating' | 'completed' | 'failed' | 'done';
  createdAt: string;
  garmentImages: GarmentImageData[];
}

export interface GarmentImageData {
  garmentImageId: number;
  imageUrl: string;
  generatedImages: GeneratedImageData[];
}

export interface GeneratedImageData {
  generatedImageId: number;
  outputUrl: string;
  poseLabel: string;
  modelId: number;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface AppState {
  models: AIModel[];
  tasks: Task[];
  currentTask: Task | null;
  generations: GenerationBatch[];
  isLoading: boolean;
  error: string | null;
}