import React from "react";
export default function VoiceControls() {
  return (
    <div className="flex justify-center items-center gap-6 py-4 bg-gray-950 border-t border-gray-800">
      <button className="bg-pink-700 hover:bg-pink-600 text-white px-5 py-2 rounded transition">🎤 Record</button>
      <button className="bg-pink-700 hover:bg-pink-600 text-white px-5 py-2 rounded transition">🔊 Play</button>
    </div>
  );
}
