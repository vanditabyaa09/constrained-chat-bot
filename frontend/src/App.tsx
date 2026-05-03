import React from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';

const App: React.FC = () => {
  return (
    <div className="flex h-screen w-full bg-[#0a0a0b] text-[#ededef] overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <ChatArea />
      </main>
    </div>
  );
};

export default App;
