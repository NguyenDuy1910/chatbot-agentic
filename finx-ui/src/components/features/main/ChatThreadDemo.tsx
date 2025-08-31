import React, { useState } from 'react';
import { ChatArea, ChatInput, Sidebar } from '@/components/features/chat';
import { Message, ChatSession } from '@/types/features/chat';
import { MessageSquare, Plus } from 'lucide-react';

export const ChatThreadDemo: React.FC = () => {
  // Demo chat sessions
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([
    {
      id: '1',
      title: 'Data Analysis Discussion',
      messages: [
        {
          id: '1',
          content: 'Hello! How can I help you with data analysis today?',
          role: 'assistant',
          timestamp: new Date(Date.now() - 3600000)
        },
        {
          id: '2',
          content: 'I need help analyzing sales data from the last quarter',
          role: 'user',
          timestamp: new Date(Date.now() - 3500000)
        },
        {
          id: '3',
          content: 'I\'d be happy to help you analyze your sales data! Could you tell me more about the specific metrics you\'re interested in? For example:\n\n• Revenue trends\n• Customer segments\n• Product performance\n• Regional analysis\n\nAlso, what format is your data in?',
          role: 'assistant',
          timestamp: new Date(Date.now() - 3400000)
        }
      ],
      createdAt: new Date(Date.now() - 3600000),
      updatedAt: new Date(Date.now() - 3400000)
    },
    {
      id: '2',
      title: 'Python Coding Help',
      messages: [
        {
          id: '4',
          content: 'I need help with Python data visualization',
          role: 'user',
          timestamp: new Date(Date.now() - 7200000)
        },
        {
          id: '5',
          content: 'I\'d be happy to help you with Python data visualization! What specific type of chart or visualization are you looking to create? Here are some popular options:\n\n• **Matplotlib**: Great for basic plots and statistical charts\n• **Seaborn**: Beautiful statistical visualizations\n• **Plotly**: Interactive charts and dashboards\n• **Bokeh**: Web-ready interactive visualizations\n\nWhat kind of data are you working with?',
          role: 'assistant',
          timestamp: new Date(Date.now() - 7100000)
        },
        {
          id: '6',
          content: 'I want to create an interactive dashboard with multiple charts',
          role: 'user',
          timestamp: new Date(Date.now() - 7000000)
        },
        {
          id: '7',
          content: 'Perfect! For interactive dashboards, I recommend **Plotly Dash** or **Streamlit**. Here\'s a quick comparison:\n\n**Plotly Dash:**\n```python\nimport dash\nfrom dash import dcc, html\nimport plotly.express as px\n\napp = dash.Dash(__name__)\n\napp.layout = html.Div([\n    dcc.Graph(figure=px.bar(df, x="category", y="value"))\n])\n```\n\n**Streamlit:**\n```python\nimport streamlit as st\nimport plotly.express as px\n\nst.title("My Dashboard")\nst.plotly_chart(px.bar(df, x="category", y="value"))\n```\n\nWhich approach interests you more?',
          role: 'assistant',
          timestamp: new Date(Date.now() - 6900000)
        }
      ],
      createdAt: new Date(Date.now() - 7200000),
      updatedAt: new Date(Date.now() - 6900000)
    },
    {
      id: '3',
      title: 'Machine Learning Project',
      messages: [
        {
          id: '8',
          content: 'Can you help me with a machine learning project for predicting customer churn?',
          role: 'user',
          timestamp: new Date(Date.now() - 10800000)
        },
        {
          id: '9',
          content: 'Absolutely! Customer churn prediction is a classic and valuable ML problem. Let\'s break this down into steps:\n\n**1. Data Collection & Understanding**\n• Customer demographics\n• Usage patterns\n• Transaction history\n• Support interactions\n• Subscription details\n\n**2. Feature Engineering**\n• Recency, Frequency, Monetary (RFM) analysis\n• Engagement metrics\n• Behavioral patterns\n\n**3. Model Selection**\n• Logistic Regression (baseline)\n• Random Forest\n• XGBoost\n• Neural Networks\n\nWhat type of business/industry is this for? And what data do you currently have available?',
          role: 'assistant',
          timestamp: new Date(Date.now() - 10700000)
        }
      ],
      createdAt: new Date(Date.now() - 10800000),
      updatedAt: new Date(Date.now() - 10700000)
    }
  ]);

  const [currentSessionId, setCurrentSessionId] = useState<string | null>('1');
  const [isLoading, setIsLoading] = useState(false);

  // Chat handlers
  const handleSendMessage = (content: string) => {
    if (!currentSessionId) return;

    const newMessage: Message = {
      id: Math.random().toString(36).substring(2, 11),
      content,
      role: 'user',
      timestamp: new Date()
    };

    setChatSessions(prev => prev.map(session => 
      session.id === currentSessionId 
        ? { 
            ...session, 
            messages: [...session.messages, newMessage],
            updatedAt: new Date()
          }
        : session
    ));

    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "That's a great question! Let me help you with that.",
        "I understand what you're looking for. Here's my analysis:",
        "Based on your input, I can provide several insights:",
        "Let me break this down for you step by step:",
        "That's an interesting challenge. Here's how I would approach it:"
      ];
      
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      
      const aiResponse: Message = {
        id: Math.random().toString(36).substring(2, 11),
        content: `${randomResponse}\n\nRegarding: "${content}"\n\nI can help you explore this topic further. What specific aspect would you like to dive deeper into?`,
        role: 'assistant',
        timestamp: new Date()
      };

      setChatSessions(prev => prev.map(session => 
        session.id === currentSessionId 
          ? { 
              ...session, 
              messages: [...session.messages, aiResponse],
              updatedAt: new Date()
            }
          : session
      ));
      setIsLoading(false);
    }, 1500);
  };

  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  const handleDeleteSession = (sessionId: string) => {
    setChatSessions(prev => prev.filter(session => session.id !== sessionId));
    if (currentSessionId === sessionId) {
      const remainingSessions = chatSessions.filter(session => session.id !== sessionId);
      setCurrentSessionId(remainingSessions.length > 0 ? remainingSessions[0].id : null);
    }
  };

  const handleNewChat = () => {
    const newSession: ChatSession = {
      id: Math.random().toString(36).substring(2, 11),
      title: 'New Conversation',
      messages: [
        {
          id: Math.random().toString(36).substring(2, 11),
          content: 'Hello! I\'m Julius, your AI assistant. How can I help you today?',
          role: 'assistant',
          timestamp: new Date()
        }
      ],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    setChatSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
  };

  const getCurrentSession = () => {
    return chatSessions.find(session => session.id === currentSessionId);
  };

  const currentSession = getCurrentSession();

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Chat Sidebar */}
      <div className="w-80 border-r border-gray-200 bg-white">
        <Sidebar
          sessions={chatSessions}
          currentSessionId={currentSessionId}
          onSelectSession={handleSelectSession}
          onDeleteSession={handleDeleteSession}
          onNewChat={handleNewChat}
        />
      </div>
      
      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {currentSession ? (
          <>
            <div className="flex-1 overflow-hidden">
              <ChatArea
                messages={currentSession.messages}
                isLoading={isLoading}
                onSendMessage={handleSendMessage}
              />
            </div>
            <div className="border-t border-gray-200 bg-white p-4">
              <ChatInput
                onSendMessage={handleSendMessage}
                placeholder="Ask Julius anything..."
                disabled={isLoading}
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">No Chat Selected</h2>
              <p className="text-gray-600 mb-6">Select a chat thread or start a new conversation</p>
              <button 
                onClick={handleNewChat}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Chat
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatThreadDemo;
