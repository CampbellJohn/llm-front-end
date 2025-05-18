import React, { useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import { useChat } from './hooks/useChat';

function App() {
  const { 
    messages, 
    isLoading, 
    isStreaming, 
    error, 
    sendMessage, 
    clearMessages, 
    loadConversation,
    currentConversationId,
    conversationTitle
  } = useChat();

  const handleSelectConversation = (conversationId) => {
    if (conversationId !== currentConversationId) {
      loadConversation(conversationId);
    }
  };

  const handleNewChat = () => {
    clearMessages();
  };
  
  // Update conversation title in the database when messages change
  useEffect(() => {
    if (currentConversationId && messages.length > 0) {
      // Get the first user message as the title if available
      const firstUserMessage = messages.find(msg => msg.role === 'user');
      if (firstUserMessage && firstUserMessage.content) {
        // Truncate long messages for the title
        const title = firstUserMessage.content.length > 30 
          ? `${firstUserMessage.content.substring(0, 30)}...` 
          : firstUserMessage.content;
        
        // We would update the conversation title here if we had that API endpoint
        // For now, just update the local state
        if (title !== conversationTitle) {
          // This would be where we call an API to update the title
          console.log(`Would update conversation ${currentConversationId} title to: ${title}`);
        }
      }
    }
  }, [messages, currentConversationId, conversationTitle]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar 
        onSelectConversation={handleSelectConversation} 
        currentConversationId={currentConversationId}
        onNewChat={handleNewChat}
      />
      
      {/* Main content */}
      <div className="flex flex-col flex-1 ml-0 md:ml-64">
        <header className="bg-white shadow z-10">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center">
            <h1 className="text-xl font-semibold text-gray-800">
              {currentConversationId ? conversationTitle : 'New Chat'}
            </h1>
          </div>
        </header>
        
        <main className="flex-grow">
          <ChatInterface 
            messages={messages}
            isLoading={isLoading}
            isStreaming={isStreaming}
            error={error}
            sendMessage={sendMessage}
            clearMessages={clearMessages}
          />
        </main>
        
        <footer className="bg-white border-t border-gray-200 py-4">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500 text-sm">
            https://github.com/CampbellJohn/llm-front-end
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;