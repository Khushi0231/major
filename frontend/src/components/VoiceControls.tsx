import React, { useState } from 'react';

interface VoiceControlsProps {
  onTranscribe: (text: string) => Promise<void>;
  onSpeak: (text: string) => Promise<void>;
}

export const VoiceControls: React.FC<VoiceControlsProps> = ({ onTranscribe, onSpeak }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleRecord = async () => {
    setIsRecording(!isRecording);
    // Voice recording logic would be implemented here
  };

  const handleSpeak = async (text: string) => {
    setIsSpeaking(true);
    await onSpeak(text);
    setIsSpeaking(false);
  };

  return (
    <div className="flex gap-3">
      <button
        onClick={handleRecord}
        className={`px-4 py-2 rounded-lg font-semibold ${
          isRecording ? 'bg-red-500 text-white' : 'bg-gray-300'
        }`}
      >
        {isRecording ? '🎙️ Stop' : '🎤 Record'}
      </button>
    </div>
  );
};
