import React, { useState, useEffect } from 'react';
import { FiPlus, FiTrash2, FiMessageSquare, FiMenu, FiX } from 'react-icons/fi';
import { fetchConversations, createConversation, deleteConversation } from '../services/api';

const Sidebar = ({ onSelectConversation, currentConversationId, onNewChat }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (mobile && isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isOpen]);

  // Fetch conversations
  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await fetchConversations();
      setConversations(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError('Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  // Load conversations initially and set up periodic refresh
  useEffect(() => {
    loadConversations();
    
    // Refresh conversations every 5 seconds
    const intervalId = setInterval(() => {
      loadConversations();
    }, 5000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);
  
  // Refresh conversations when currentConversationId changes
  useEffect(() => {
    loadConversations();
  }, [currentConversationId]);

  // Create new conversation
  const handleNewChat = async () => {
    try {
      const newTitle = `New Chat ${new Date().toLocaleString()}`;
      const newConversation = await createConversation(newTitle);
      setConversations(prev => [newConversation, ...prev]);
      onSelectConversation(newConversation.id);
      onNewChat();
    } catch (err) {
      console.error('Failed to create new conversation:', err);
      setError('Failed to create new conversation');
    }
  };

  // Delete conversation
  const handleDeleteConversation = async (e, id) => {
    e.stopPropagation();
    try {
      await deleteConversation(id);
      setConversations(prev => prev.filter(conv => conv.id !== id));
      if (id === currentConversationId) {
        onNewChat();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError('Failed to delete conversation');
    }
  };

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Mobile menu button */}
      {isMobile && (
        <button 
          onClick={toggleSidebar}
          className="fixed top-4 left-4 z-50 p-2 bg-gray-800 text-white rounded-md"
        >
          {isOpen ? <FiX size={20} /> : <FiMenu size={20} />}
        </button>
      )}

      {/* Sidebar */}
      <div className={`
        fixed top-0 left-0 h-full bg-gray-900 text-white transition-all duration-300 ease-in-out z-40
        ${isOpen ? 'w-64' : 'w-0'} 
        ${isMobile ? 'shadow-lg' : ''}
      `}>
        <div className="flex flex-col h-full">
          {/* New chat button */}
          <div className="p-4">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-white/10 hover:bg-white/20 rounded-md transition-colors"
            >
              <FiPlus size={16} />
              <span>New chat</span>
            </button>
          </div>

          {/* Conversations list */}
          <div className="flex-grow overflow-y-auto">
            {loading ? (
              <div className="p-4 text-gray-400 text-center">Loading...</div>
            ) : error ? (
              <div className="p-4 text-red-400 text-center">{error}</div>
            ) : conversations.length === 0 ? (
              <div className="p-4 text-gray-400 text-center">No conversations yet</div>
            ) : (
              <ul className="space-y-1 px-2">
                {conversations.map((conversation) => (
                  <li 
                    key={conversation.id}
                    onClick={() => onSelectConversation(conversation.id)}
                    className={`
                      flex items-center justify-between p-3 rounded-md cursor-pointer group
                      ${currentConversationId === conversation.id ? 'bg-white/20' : 'hover:bg-white/10'}
                    `}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FiMessageSquare size={16} />
                      <span className="truncate">{conversation.title}</span>
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(e, conversation.id)}
                      className="opacity-0 group-hover:opacity-100 hover:text-red-400"
                      aria-label="Delete conversation"
                    >
                      <FiTrash2 size={16} />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-white/20 text-xs text-gray-400">
            <p>LLM Chat App</p>
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isMobile && isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30"
          onClick={toggleSidebar}
        />
      )}
    </>
  );
};

export default Sidebar;
