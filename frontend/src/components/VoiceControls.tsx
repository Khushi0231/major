import React, { useState, useRef } from "react";
import { speechToText } from "../utils/api";

export default function VoiceControls() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        setIsProcessing(true);
        
        try {
          const audioFile = new File([audioBlob], "recording.wav", { type: "audio/wav" });
          const result = await speechToText(audioFile);
          
          if (result.success && result.text) {
            // Could auto-fill chat input here
            alert(`Transcribed: ${result.text}`);
          }
        } catch (error) {
          console.error("STT error:", error);
        } finally {
          setIsProcessing(false);
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Recording error:", error);
      alert("Microphone access denied");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="border-t border-gray-800/50 bg-[#0f0f23]/80 p-4">
      <div className="max-w-4xl mx-auto flex justify-center">
        <button
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium transition-all ${
            isRecording
              ? "bg-red-600 hover:bg-red-700 text-white"
              : "bg-gray-800/50 hover:bg-gray-800 text-gray-300 border border-gray-700/50"
          } disabled:opacity-50`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
        >
          {isProcessing ? "⏳ Processing..." : isRecording ? "⏹️ Stop" : "🎤 Record"}
        </button>
      </div>
    </div>
  );
}
