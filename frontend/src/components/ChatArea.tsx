import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Search, Bot, User, CornerDownLeft, Plus, FileQuestion, XCircle, CheckCircle2 } from 'lucide-react';
import { useChatStore } from '../store/useChatStore';

const ChatArea: React.FC = () => {
  const { messages, isLoading, sendMessage, clearChat, pdfMeta, toast, uploadPDF } = useChatStore();
  const [query, setQuery] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = () => {
    if (query.trim() && !isLoading) {
      sendMessage(query.trim());
      setQuery('');
      if (textareaRef.current) textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadPDF(e.target.files[0]);
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0a0a0b] relative overflow-hidden">
      {/* Topbar */}
      <header className="h-[52px] border-b border-[#1f1f23] flex items-center justify-between px-6 bg-[#0a0a0b]/80 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          {pdfMeta ? (
            <div className="flex items-center gap-2 bg-[#18181b] px-3 py-1 rounded-full border border-[#2e2e35]">
              <div className="w-1.5 h-1.5 bg-[#5b5bd6] rounded-full"></div>
              <span className="text-xs font-medium text-[#ededef]">{pdfMeta.filename}</span>
            </div>
          ) : (
            <span className="text-xs text-[#52525b]">No document loaded</span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <button onClick={clearChat} className="p-2 text-[#52525b] hover:text-[#f87171] transition-colors rounded-lg hover:bg-[#18181b]" title="Clear chat">
            <Trash2 size={18} />
          </button>
          <button className="p-2 text-[#52525b] hover:text-[#ededef] transition-colors rounded-lg hover:bg-[#18181b]">
            <Search size={18} />
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-8 space-y-8 scroll-smooth">
        {!pdfMeta && (
          <div className="h-full flex flex-col items-center justify-center animate-fade-in-up">
            <div className="w-20 h-20 bg-[#18181b] border border-[#2e2e35] rounded-3xl flex items-center justify-center mb-6 shadow-2xl">
              <FileQuestion size={40} className="text-[#52525b]" />
            </div>
            <h2 className="text-xl font-semibold text-[#ededef] mb-2">No document loaded</h2>
            <p className="text-sm text-[#a1a1aa] text-center max-w-xs mb-8">
              Upload a PDF from the sidebar to start chatting with your documents.
            </p>
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-[#2e2e35] hover:border-[#5b5bd6]/50 rounded-2xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer transition-all bg-[#18181b]/50 group w-full max-w-xs"
            >
              <Plus className="text-[#52525b] group-hover:text-[#5b5bd6]" />
              <span className="text-sm font-medium text-[#ededef]">Upload PDF</span>
            </div>
          </div>
        )}

        {pdfMeta && messages.length === 0 && !isLoading && (
          <div className="h-full flex flex-col items-center justify-center opacity-40">
            <Bot size={48} className="mb-4 text-[#5b5bd6]" />
            <p className="text-sm">Start asking questions about {pdfMeta.filename}.</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
          >
            <div className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                msg.role === 'user' ? 'bg-[#5b5bd6] text-white' : 'bg-[#18181b] border border-[#2e2e35] text-[#5b5bd6]'
              }`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              
              <div className="space-y-2">
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user' 
                    ? 'bg-[#5b5bd6] text-white' 
                    : 'bg-[#18181b] border border-[#2e2e35] text-[#ededef]'
                } ${msg.inScope === false && msg.role === 'assistant' ? 'text-[#f87171] border-[#f87171]/20' : ''}`}>
                  {msg.content}
                </div>
                
                {msg.citations && msg.citations.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {msg.citations.map((page, pIdx) => (
                      <button 
                        key={pIdx} 
                        onClick={() => console.log(`Navigating to Page ${page}`)}
                        className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#5b5bd6]/10 text-[#5b5bd6] border border-[#5b5bd6]/20 hover:bg-[#5b5bd6]/20 transition-colors"
                      >
                        Page {page}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start animate-fade-in-up">
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-lg bg-[#18181b] border border-[#2e2e35] flex items-center justify-center text-[#5b5bd6]">
                <Bot size={16} />
              </div>
              <div className="bg-[#18181b] border border-[#2e2e35] rounded-2xl px-4 py-3 flex gap-1 items-center">
                <div className="w-1.5 h-1.5 bg-[#5b5bd6] rounded-full dot-pulse stagger-1"></div>
                <div className="w-1.5 h-1.5 bg-[#5b5bd6] rounded-full dot-pulse stagger-2"></div>
                <div className="w-1.5 h-1.5 bg-[#5b5bd6] rounded-full dot-pulse stagger-3"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Row */}
      <div className="p-6 bg-gradient-to-t from-[#0a0a0b] via-[#0a0a0b] to-transparent">
        <div className="max-w-4xl mx-auto relative group">
          <div className={`relative flex items-end gap-2 bg-[#18181b] border ${query ? 'border-[#5b5bd6]' : 'border-[#2e2e35]'} rounded-xl p-2 transition-all shadow-2xl shadow-black/50 focus-within:ring-1 focus-within:ring-[#5b5bd6]/30`}>
            <textarea
              ref={textareaRef}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                adjustTextareaHeight();
              }}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about the document..."
              className="flex-1 bg-transparent border-none focus:ring-0 text-sm py-2 px-3 resize-none min-h-[40px] max-h-[160px] text-[#ededef] placeholder-[#52525b]"
              rows={1}
            />
            <button
              onClick={handleSend}
              disabled={!query.trim() || isLoading}
              className={`p-2 rounded-lg transition-all ${
                query.trim() && !isLoading 
                  ? 'bg-[#5b5bd6] text-white shadow-lg shadow-[#5b5bd6]/40 hover:scale-105 active:scale-95' 
                  : 'bg-[#1f1f23] text-[#52525b] cursor-not-allowed'
              }`}
            >
              <Send size={20} />
            </button>
          </div>
          <div className="mt-2 flex items-center justify-between px-2">
            <span className="text-[10px] text-[#52525b] flex items-center gap-1">
              <CornerDownLeft size={10} />
              {navigator.platform.toUpperCase().indexOf('MAC') >= 0 ? '⌘' : 'Ctrl'} + Enter to send
            </span>
          </div>
        </div>
      </div>

      {/* Floating Action Button (Mobile Only) */}
      <div className="sm:hidden fixed bottom-24 right-6 z-20">
        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".pdf" />
        <button 
          onClick={() => fileInputRef.current?.click()}
          className="w-14 h-14 bg-[#5b5bd6] rounded-full shadow-2xl shadow-[#5b5bd6]/40 flex items-center justify-center text-white active:scale-90 transition-transform"
        >
          <Plus size={28} />
        </button>
      </div>

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 animate-fade-in-up">
          <div className={`px-4 py-3 rounded-xl border flex items-center gap-3 shadow-2xl backdrop-blur-md ${
            toast.type === 'success' 
              ? 'bg-green-500/10 border-green-500/20 text-green-400' 
              : 'bg-red-500/10 border-red-500/20 text-red-400'
          }`}>
            {toast.type === 'success' ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
            <span className="text-sm font-medium">{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatArea;
