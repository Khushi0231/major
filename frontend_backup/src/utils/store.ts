import { Message, Document } from '../types';

export interface AppState {
  messages: Message[];
  documents: Document[];
  isLoading: boolean;
  error: string | null;
}

const initialState: AppState = {
  messages: [],
  documents: [],
  isLoading: false,
  error: null,
};

let appState = initialState;
const listeners: Set<(state: AppState) => void> = new Set();

export const store = {
  getState: () => appState,
  
  setState: (updates: Partial<AppState>) => {
    appState = { ...appState, ...updates };
    listeners.forEach(listener => listener(appState));
  },

  subscribe: (listener: (state: AppState) => void) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  addMessage: (message: Message) => {
    store.setState({ messages: [...appState.messages, message] });
  },

  addDocument: (doc: Document) => {
    store.setState({ documents: [...appState.documents, doc] });
  },

  setLoading: (isLoading: boolean) => {
    store.setState({ isLoading });
  },

  setError: (error: string | null) => {
    store.setState({ error });
  },

  clearMessages: () => {
    store.setState({ messages: [] });
  },
};
