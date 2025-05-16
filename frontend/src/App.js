import React from 'react';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center">
          <h1 className="text-xl font-semibold text-gray-800">LLM Chat</h1>
        </div>
      </header>
      
      <main className="flex-grow">
        <ChatInterface />
      </main>
      
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500 text-sm">
          https://github.com/CampbellJohn/llm-front-end
        </div>
      </footer>
    </div>
  );
}

export default App;