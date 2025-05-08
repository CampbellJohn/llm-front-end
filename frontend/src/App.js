import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import ModelSelector from './components/ModelSelector';
import { fetchModels, fetchDefaultConfig } from './services/api';

function App() {
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initializeApp = async () => {
      try {
        setLoading(true);
        
        // Fetch available models
        const models = await fetchModels();
        setAvailableModels(models);
        
        // Fetch default configuration
        const defaultConfig = await fetchDefaultConfig();
        setSelectedProvider(defaultConfig.provider);
        setSelectedModel(defaultConfig.model);
        
        setLoading(false);
      } catch (err) {
        console.error('Error initializing app:', err);
        setError('Failed to load application data. Please check your connection and try again.');
        setLoading(false);
      }
    };
    
    initializeApp();
  }, []);

  const handleModelChange = (modelId, provider) => {
    setSelectedModel(modelId);
    setSelectedProvider(provider);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-t-4 border-blue-500 border-solid rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-gray-700">Loading application...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-50 p-6 rounded-lg border border-red-200 max-w-md">
          <h2 className="text-red-700 text-xl font-semibold mb-2">Error</h2>
          <p className="text-red-600">{error}</p>
          <button 
            className="mt-4 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-800">LLM Chat</h1>
          <ModelSelector 
            models={availableModels}
            selectedModel={selectedModel}
            onModelChange={handleModelChange}
          />
        </div>
      </header>
      
      <main className="flex-grow">
        <ChatInterface 
          selectedModel={selectedModel}
          selectedProvider={selectedProvider}
        />
      </main>
      
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500 text-sm">
          Powered by Anthropic Claude and OpenAI GPT
        </div>
      </footer>
    </div>
  );
}

export default App;