import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AppState, AIModel, Task, GenerationBatch } from '../../types';
import { appAPI } from '../../services/api';

const initialState: AppState = {
  models: [],
  tasks: [],
  currentTask: null,
  generations: [],
  isLoading: false,
  error: null,
};

export const fetchTasks = createAsyncThunk('app/fetchTasks', async () => {
  return await appAPI.getTasks();
});

export const fetchModels = createAsyncThunk('app/fetchModels', async () => {
  return await appAPI.getModels();
});

export const createTask = createAsyncThunk(
  'app/createTask',
  async (taskData: { 
    name: string; 
    description?: string; 
    modelId: string; 
    garmentType: 'top' | 'bottom' | 'onepiece';
    pose?: string;
  }) => {
    return await appAPI.createTask(taskData);
  }
);

export const uploadModel = createAsyncThunk(
  'app/uploadModel',
  async (modelData: { name: string; images: File[] }) => {
    if (!modelData.name) {
      throw new Error("Model name is required.");
    }
    if (!modelData.images || !Array.isArray(modelData.images) || modelData.images.length === 0) {
      throw new Error("At least one image (File) is required.");
    }
    // Optionally check all images are File objects
    if (!modelData.images.every(f => f instanceof File)) {
      throw new Error("All images must be valid File objects.");
    }
    return await appAPI.uploadModel(modelData);
  }
);

export const generateImages = createAsyncThunk(
  'app/generateImages',
  async ({ taskId, garmentImages }: { taskId: string; garmentImages: File[] }) => {
    const result = await appAPI.generateImages(taskId, garmentImages);
    return result;
  }
);

export const fetchTaskBatches = createAsyncThunk(
  'app/fetchTaskBatches',
  async (taskId: string) => {
    return await appAPI.getTaskBatches(taskId);
  }
);

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setCurrentTask: (state, action: PayloadAction<Task | null>) => {
      state.currentTask = action.payload;
    },
    addGenerationBatch: (state, action: PayloadAction<GenerationBatch>) => {
      state.generations.push(action.payload);
    },
    updateGenerationStatus: (state, action: PayloadAction<{ batchId: string; status: string }>) => {
      const batch = state.generations.find(g => g.id === action.payload.batchId);
      if (batch) {
        batch.status = action.payload.status as any;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTasks.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.isLoading = false;
        state.tasks = action.payload;
      })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch tasks';
      })
      .addCase(fetchModels.fulfilled, (state, action) => {
        state.models = action.payload;
      })
      .addCase(createTask.fulfilled, (state, action) => {
        state.tasks.push(action.payload);
        state.currentTask = action.payload;
      })
      .addCase(uploadModel.fulfilled, (state, action) => {
        state.models.push(action.payload);
      })
      .addCase(generateImages.fulfilled, (state, action) => {
        state.generations.push(action.payload);
      })
      .addCase(fetchTaskBatches.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchTaskBatches.fulfilled, (state, action) => {
        state.isLoading = false;
        state.generations = action.payload;
      })
      .addCase(fetchTaskBatches.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch task batches';
      });
  },
});

export const { setCurrentTask, addGenerationBatch, updateGenerationStatus } = appSlice.actions;
export default appSlice.reducer;