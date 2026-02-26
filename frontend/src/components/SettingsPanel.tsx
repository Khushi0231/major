import { useState, useEffect } from "react";
import { setPIN, checkPINExists } from "../utils/api";
import './SettingsPanel.css';

interface SettingsPanelProps {
  theme: "dark" | "light";
  setTheme: (t: "dark" | "light") => void;
  onLockApp?: () => void;
}

export default function SettingsPanel({ theme, setTheme, onLockApp }: SettingsPanelProps) {
  const [pinExists, setPinExists] = useState(false);
  const [pinInput, setPinInput] = useState("");
  const [confirmPin, setConfirmPin] = useState("");
  const [pinMode, setPinMode] = useState<"set" | "change" | "none">("none");
  const [message, setMessage] = useState("");
  const [msgType, setMsgType] = useState<"success" | "error">("success");

  useEffect(() => { checkPinStatus(); }, []);

  const checkPinStatus = async () => {
    try {
      const result = await checkPINExists();
      setPinExists(result.exists);
    } catch {
      // Backend might use localStorage fallback
      setPinExists(!!localStorage.getItem("dravis_pin"));
    }
  };

  const handleSetPIN = async () => {
    if (pinInput.length !== 4 || !/^\d{4}$/.test(pinInput)) {
      setMessage("PIN must be exactly 4 digits"); setMsgType("error"); return;
    }
    if (pinInput !== confirmPin) {
      setMessage("PINs do not match"); setMsgType("error"); return;
    }
    try {
      await setPIN(pinInput);
    } catch {
      // Fallback: store PIN hash locally
      localStorage.setItem("dravis_pin", btoa(pinInput));
    }
    setMessage("PIN set successfully!");
    setMsgType("success");
    setPinInput(""); setConfirmPin("");
    setPinExists(true); setPinMode("none");
  };

  const handleRemovePIN = () => {
    localStorage.removeItem("dravis_pin");
    setPinExists(false);
    setMessage("PIN removed");
    setMsgType("success");
  };

  return (
    <div className="settings-panel">
      {/* Appearance */}
      <div className="settings-card">
        <h3 className="settings-card-title">Appearance</h3>
        <div className="theme-toggle">
          <button className={`theme-btn-opt ${theme === "dark" ? "active" : ""}`} onClick={() => setTheme("dark")}>
            🌙 Dark
          </button>
          <button className={`theme-btn-opt ${theme === "light" ? "active" : ""}`} onClick={() => setTheme("light")}>
            ☀️ Light
          </button>
        </div>
      </div>

      {/* Security */}
      <div className="settings-card">
        <h3 className="settings-card-title">Security</h3>
        {pinExists ? (
          <div className="pin-section">
            <div className="pin-status">
              <span className="pin-badge active">🔒 PIN Active</span>
              <div className="pin-actions">
                <button className="settings-btn secondary" onClick={handleRemovePIN}>Remove PIN</button>
                {onLockApp && <button className="settings-btn primary" onClick={onLockApp}>Lock Now</button>}
              </div>
            </div>
          </div>
        ) : pinMode === "set" ? (
          <div className="pin-form">
            <input
              type="password" maxLength={4} placeholder="Enter 4-digit PIN"
              value={pinInput} autoFocus
              onChange={(e) => setPinInput(e.target.value.replace(/\D/g, ""))}
              className="settings-input"
            />
            <input
              type="password" maxLength={4} placeholder="Confirm PIN"
              value={confirmPin}
              onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, ""))}
              className="settings-input"
            />
            <div className="pin-form-actions">
              <button className="settings-btn primary" onClick={handleSetPIN}>Set PIN</button>
              <button className="settings-btn secondary" onClick={() => { setPinMode("none"); setPinInput(""); setConfirmPin(""); setMessage(""); }}>Cancel</button>
            </div>
          </div>
        ) : (
          <div className="pin-section">
            <span className="pin-badge">🔓 No PIN set</span>
            <button className="settings-btn primary" onClick={() => setPinMode("set")}>Set PIN</button>
          </div>
        )}
        {message && <div className={`settings-msg ${msgType}`}>{message}</div>}
      </div>

      {/* About */}
      <div className="settings-card">
        <h3 className="settings-card-title">About</h3>
        <div className="about-info">
          <div className="about-logo">D</div>
          <div>
            <div className="about-name">DRAVIS</div>
            <div className="about-desc">Dynamic Reasoning AI for Virtual Intelligent Study</div>
            <div className="about-meta">Version 1.0.0 · 100% Offline AI Study Assistant</div>
          </div>
        </div>
      </div>
    </div>
  );
}
