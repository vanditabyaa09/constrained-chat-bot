import { create } from 'zustand';
import * as api from '../api/client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: number[];
  inScope?: boolean;
}

interface PDFMeta {
  filename: string;
  pages: number;
  chunks: number;
}

interface Toast {
  message: string;
  type: 'success' | 'error';
  id: number;
}

interface ChatState {
  pdfMeta: PDFMeta | null;
  messages: Message[];
  isLoading: boolean;
  toast: Toast | null;
  uploadPDF: (file: File) => Promise<void>;
  sendMessage: (query: string) => Promise<void>;
  clearChat: () => void;
  resetPDF: () => Promise<void>;
  showToast: (message: string, type: 'success' | 'error') => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  pdfMeta: null,
  messages: [],
  isLoading: false,
  toast: null,

  showToast: (message, type) => {
    const id = Date.now();
    set({ toast: { message, type, id } });
    setTimeout(() => {
      if (get().toast?.id === id) {
        set({ toast: null });
      }
    }, 3000);
  },

  uploadPDF: async (file) => {
    set({ isLoading: true });
    try {
      const data = await api.uploadPDF(file);
      const welcomeMessage: Message = {
        role: 'assistant',
        content: `I've indexed ${data.filename} (${data.pages} pages, ${data.chunks} chunks). Ask me anything about it — I'll always tell you which page my answer comes from.`
      };
      set({ 
        pdfMeta: data, 
        messages: [welcomeMessage], 
        isLoading: false 
      });
      get().showToast('PDF uploaded and indexed successfully!', 'success');
    } catch (error) {
      console.error('Upload failed', error);
      set({ isLoading: false });
      get().showToast('Failed to upload PDF. Please try again.', 'error');
    }
  },

  sendMessage: async (query) => {
    const { messages } = get();
    const newUserMessage: Message = { role: 'user', content: query };
    
    set({ 
      messages: [...messages, newUserMessage],
      isLoading: true 
    });

    try {
      // Get last 6 messages for history context
      const history = messages.slice(-6).map(m => ({
        role: m.role,
        content: m.content
      }));

      const data = await api.chat(query, history);
      
      const botMessage: Message = {
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        inScope: data.in_scope
      };

      set({ 
        messages: [...get().messages, botMessage],
        isLoading: false 
      });
    } catch (error) {
      console.error('Chat failed', error);
      set({ isLoading: false });
    }
  },

  clearChat: () => set({ messages: [] }),

  resetPDF: async () => {
    try {
      await api.reset();
      set({ pdfMeta: null, messages: [] });
    } catch (error) {
      console.error('Reset failed', error);
    }
  },
}));
