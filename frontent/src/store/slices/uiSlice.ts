import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface UIState {
  globalError: string | null;
}

const initialState: UIState = {
  globalError: null,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setGlobalError: (state, action: PayloadAction<string | null>) => {
      state.globalError = action.payload;
    },
    clearGlobalError: (state) => {
      state.globalError = null;
    },
  },
});

export const { setGlobalError, clearGlobalError } = uiSlice.actions;
export default uiSlice.reducer;


