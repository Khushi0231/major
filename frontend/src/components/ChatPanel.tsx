import React, { useState } from 'react';
import { Message } from '../types';

interface ChatPanelProps {
  messages: Message[];
  onSendMessage: (text: string) => Promise<void>;
  isLoading: boolean;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ messages, onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    await onSendMessage(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-black'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && <div className="text-gray-500">Loading...</div>}
      </div>
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none"
          />
          <button
            onClick={handleSend}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};
