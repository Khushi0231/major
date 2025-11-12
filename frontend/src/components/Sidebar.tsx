import React from 'react';

interface SidebarProps {
  documents: string[];
  onNewChat: () => void;
  onSelectDocument: (doc: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ documents, onNewChat, onSelectDocument }) => {
  return (
    <div className="w-64 bg-gray-900 text-white p-4 flex flex-col">
      <button
        onClick={onNewChat}
        className="w-full mb-6 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold"
      >
        + New Chat
      </button>
      <h2 className="text-lg font-bold mb-4">Documents</h2>
      <div className="flex-1 overflow-y-auto space-y-2">
        {documents.map((doc, idx) => (
          <div
            key={idx}
            onClick={() => onSelectDocument(doc)}
            className="p-2 bg-gray-800 hover:bg-gray-700 rounded cursor-pointer truncate"
            title={doc}
          >
            {doc}
          </div>
        ))}
      </div>
    </div>
  );
};
