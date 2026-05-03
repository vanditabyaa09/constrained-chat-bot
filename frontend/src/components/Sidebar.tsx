import React, { useRef } from 'react';
import { FileText, Upload, Database, Layers } from 'lucide-react';
import { useChatStore } from '../store/useChatStore';

const Sidebar: React.FC = () => {
  const { pdfMeta, uploadPDF, isLoading } = useChatStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadPDF(e.target.files[0]);
    }
  };

  return (
    <aside className="hidden sm:flex w-[260px] bg-[#0f0f12] border-r border-[#1f1f23] flex-col h-full shrink-0">
      {/* Logo */}
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-[#5b5bd6] rounded-md flex items-center justify-center shadow-lg shadow-[#5b5bd6]/20">
          <Layers className="text-white w-5 h-5" />
        </div>
        <span className="font-semibold text-lg tracking-tight text-[#ededef]">DocChat</span>
      </div>

      <div className="px-6 py-2">
        <span className="text-[11px] uppercase font-bold text-[#52525b] tracking-wider">Document</span>
      </div>

      <div className="flex-1 px-4 py-2 overflow-y-auto space-y-4">
        {pdfMeta ? (
          <div className="bg-[#18181b] border border-[#2e2e35] rounded-xl p-4 space-y-4 animate-fade-in-up">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-[#5b5bd6]/10 rounded-lg">
                <FileText className="text-[#5b5bd6] w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-[#ededef] truncate">{pdfMeta.filename}</p>
                <p className="text-xs text-[#a1a1aa] mt-0.5">PDF Document</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="bg-[#0a0a0b] rounded-lg p-2 border border-[#1f1f23]">
                <p className="text-[10px] text-[#52525b] uppercase font-bold">Pages</p>
                <p className="text-sm font-semibold text-[#ededef]">{pdfMeta.pages}</p>
              </div>
              <div className="bg-[#0a0a0b] rounded-lg p-2 border border-[#1f1f23]">
                <p className="text-[10px] text-[#52525b] uppercase font-bold">Chunks</p>
                <p className="text-sm font-semibold text-[#ededef]">{pdfMeta.chunks}</p>
              </div>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <div className="w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
              <span className="text-xs font-medium text-[#a1a1aa]">Ready to answer</span>
            </div>
          </div>
        ) : (
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-[#2e2e35] hover:border-[#5b5bd6]/50 rounded-xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer transition-all bg-[#18181b]/50 group"
          >
            <div className="p-3 bg-[#1f1f23] rounded-full group-hover:bg-[#5b5bd6]/10 transition-colors">
              <Upload className="text-[#52525b] group-hover:text-[#5b5bd6] w-6 h-6" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-[#ededef]">Upload new PDF</p>
              <p className="text-xs text-[#52525b] mt-1">Drag & drop or click</p>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Upload Section */}
      <div className="p-4 border-t border-[#1f1f23]">
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          className="hidden" 
          accept=".pdf"
        />
        <button 
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className="w-full py-2.5 bg-[#18181b] hover:bg-[#1f1f23] border border-[#2e2e35] rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-all text-[#a1a1aa] hover:text-[#ededef]"
        >
          <Database className="w-4 h-4" />
          Change Source
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
