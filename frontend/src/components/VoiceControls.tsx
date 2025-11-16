import React from "react";

export default function VoiceControls(){
  // placeholder - offline voice integrations (VOSK, TTS) plug here
  return (
    <div style={{marginTop:12}}>
      <div className="p-3 bg-white/5 rounded flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button className="btn small">🎤</button>
          <div className="kv">Voice: offline (VOSK) ready</div>
        </div>
        <div className="kv">Text-to-speech: available (local)</div>
      </div>
    </div>
  );
}