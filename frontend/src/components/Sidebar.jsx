import React, { useState, useEffect } from 'react';
import { FiPlus, FiTrash2, FiMessageSquare, FiMenu, FiX } from 'react-icons/fi';
import { fetchConversations, deleteConversation } from '../services/api';

const Sidebar = ({ onSelectConversation, currentConversationId, onNewChat, refreshTrigger }) => {
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
      
      // Close sidebar when switching to mobile
      if (mobile && isOpen) {
        setIsOpen(false);
      }
      
      // Open sidebar when switching to desktop
      if (!mobile && !isOpen) {
        setIsOpen(true);
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
      
      // Log the conversations we're receiving
      console.log(`Fetched ${data.length} conversations:`, data.map(c => ({ id: c.id, title: c.title })));
      
      // Check for potential duplicates
      const ids = data.map(c => c.id);
      const uniqueIds = [...new Set(ids)];
      if (ids.length !== uniqueIds.length) {
        console.warn('Warning: Duplicate conversation IDs detected in response', 
          ids.filter((id, index) => ids.indexOf(id) !== index));
      }
      
      setConversations(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError('Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  // Load conversations initially
  useEffect(() => {
    loadConversations();
  }, []);
  
  // Refresh conversations when refreshTrigger changes (which happens when a new conversation is created)
  useEffect(() => {
    if (refreshTrigger) {
      console.log('Refreshing conversations due to refreshTrigger change:', refreshTrigger);
      loadConversations();
    }
  }, [refreshTrigger]);

  // Create new conversation
  const handleNewChat = async () => {
    try {
      // Just call onNewChat to clear the current conversation in useChat
      // This will allow useChat to create a new conversation when a message is sent
      onNewChat();
      
      // Refresh the conversation list to show any changes
      await loadConversations();
    } catch (err) {
      console.error('Failed to handle new chat:', err);
      setError('Failed to create new conversation');
    }
  };

  // Delete conversation
  const handleDeleteConversation = async (e, id) => {
    e.stopPropagation();
    
    // Show confirmation dialog
    const isConfirmed = window.confirm('Are you sure you want to delete this conversation?');
    if (!isConfirmed) {
      return; // User cancelled the deletion
    }
    
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
          className={`fixed ${isOpen ? 'top-4 right-4' : 'top-4 left-4'} z-50 p-2 rounded-md`}
          style={{ backgroundColor: '#25293c', color: '#f9fefc' }}
        >
          {isOpen ? <FiX size={20} /> : <FiMenu size={20} />}
        </button>
      )}

      {/* Sidebar */}
      <div className={`
        fixed top-0 left-0 h-full transition-all duration-300 ease-in-out z-40
        ${isOpen ? 'w-64' : 'w-0'} 
        ${isMobile ? 'shadow-lg' : ''}
        overflow-hidden
      `} style={{ backgroundColor: '#25293c', color: '#f9fefc' }}>
        <div className="flex flex-col h-full w-64">
          {/* New chat button */}
          <div className="p-4">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-md transition-colors"
              style={{ backgroundColor: '#f9b414', color: '#25293c' }}
            >
              <FiPlus size={16} />
              <span>New chat</span>
            </button>
          </div>

          {/* Conversations list */}
          <div className="flex-grow overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center" style={{ color: '#f9b414' }}>Loading...</div>
            ) : error ? (
              <div className="p-4 text-center" style={{ color: '#f9b414' }}>{error}</div>
            ) : conversations.length === 0 ? (
              <div className="p-4 text-center" style={{ color: '#f9b414' }}>No conversations yet</div>
            ) : (
              <ul className="space-y-1 px-2">
                {conversations
                  .sort((a, b) => {
                    // First, put the current conversation at the top
                    if (a.id === currentConversationId) return -1;
                    if (b.id === currentConversationId) return 1;
                    
                    // Then sort by updated_at (most recent first)
                    const dateA = new Date(a.updated_at);
                    const dateB = new Date(b.updated_at);
                    return dateB - dateA;
                  })
                  .map((conversation) => (
                  <li 
                    key={conversation.id}
                    data-conversation-id={conversation.id}
                    onClick={() => onSelectConversation(conversation.id)}
                    className={`
                      flex items-center justify-between p-3 rounded-md cursor-pointer group
                    `}
                    style={{
                      backgroundColor: currentConversationId === conversation.id ? '#e6d7a9' : 'transparent',
                      color: currentConversationId === conversation.id ? '#25293c' : '#f9fefc',
                      transition: 'background-color 0.2s'
                    }}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FiMessageSquare size={16} />
                      <span className="truncate">{conversation.title}</span>
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(e, conversation.id)}
                      className="opacity-0 group-hover:opacity-100"
                      style={{ color: currentConversationId === conversation.id ? '#25293c' : '#f9fefc', transition: 'color 0.2s' }}
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
          <div className="p-4 text-xs" style={{ borderTop: '1px solid #6e7288', color: '#f9b414' }}>
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
