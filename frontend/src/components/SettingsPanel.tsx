import { useState, useEffect } from "react";
import { setPIN, verifyPIN, checkPINExists } from "../utils/api";
import './SettingsPanel.css';

interface SettingsPanelProps {
  theme: "dark" | "light";
  setTheme: (t: "dark" | "light") => void;
  onLockApp?: () => void;
}

export default function SettingsPanel({
  theme,
  setTheme,
}: SettingsPanelProps) {
  const [pinExists, setPinExists] = useState(false);
  const [pinInput, setPinInput] = useState("");
  const [confirmPin, setConfirmPin] = useState("");
  const [pinMode, setPinMode] = useState<"set" | "verify" | "none">("none");
  const [message, setMessage] = useState("");

  useEffect(() => {
    checkPinStatus();
  }, []);

  const checkPinStatus = async () => {
    try {
      const result = await checkPINExists();
      setPinExists(result.exists);
      setPinMode(result.exists ? "none" : "set");
    } catch (error) {
      console.error("Failed to check PIN status:", error);
    }
  };

  const handleSetPIN = async () => {
    if (pinInput.length !== 4 || !/^\d{4}$/.test(pinInput)) {
      setMessage("PIN must be exactly 4 digits");
      return;
    }

    if (pinInput !== confirmPin) {
      setMessage("PINs do not match");
      return;
    }

    try {
      await setPIN(pinInput);
      setMessage("PIN set successfully!");
      setPinInput("");
      setConfirmPin("");
      setPinExists(true);
      setPinMode("none");
    } catch (error) {
      setMessage("Error setting PIN: " + (error instanceof Error ? error.message : "Unknown error"));
    }
  };

  const handleVerifyPIN = async () => {
    if (pinInput.length !== 4 || !/^\d{4}$/.test(pinInput)) {
      setMessage("PIN must be exactly 4 digits");
      return;
    }

    try {
      const result = await verifyPIN(pinInput);
      if (result && result.verified) {
        setMessage("PIN verified!");
        setPinInput("");
        setPinMode("none");
      } else {
        setMessage("Incorrect PIN");
        setPinInput("");
      }
    } catch (error) {
      setMessage("Error verifying PIN: " + (error instanceof Error ? error.message : "Unknown error"));
    }
  };

  return (
    <div className="settings-panel">
      <div className="settings-header">
        <div className="settings-title">Settings</div>
      </div>

      <div className="settings-content">
        {/* Theme Settings */}
        <div className="settings-group">
          <div className="group-title">🎨 Appearance</div>
          <div className="setting-item">
            <div>
              <div className="setting-label">Theme</div>
              <div className="setting-description">Choose your preferred color scheme</div>
            </div>
            <div className="pin-buttons" style={{ flex: 'none' }}>
              <button
                className={`pin-btn ${theme === "dark" ? "" : "secondary"}`}
                onClick={() => setTheme("dark")}
              >
                🌙 Dark
              </button>
              <button
                className={`pin-btn ${theme === "light" ? "" : "secondary"}`}
                onClick={() => setTheme("light")}
              >
                ☀️ Light
              </button>
            </div>
          </div>
        </div>

        {/* PIN Settings */}
        <div className="settings-group">
          <div className="group-title">🔒 Security</div>
          {pinExists ? (
            <div>
              <div className="setting-item">
                <div>
                  <div className="setting-label">PIN Lock</div>
                  <div className="setting-description">PIN is set</div>
                </div>
              </div>
              {pinMode === "verify" ? (
                <div className="pin-section">
                  <input
                    type="password"
                    maxLength={4}
                    placeholder="Enter 4-digit PIN"
                    value={pinInput}
                    onChange={(e) => setPinInput(e.target.value.replace(/\D/g, ""))}
                    className="pin-input"
                  />
                  <div className="pin-buttons">
                    <button className="pin-btn" onClick={handleVerifyPIN}>
                      Verify
                    </button>
                    <button
                      className="pin-btn secondary"
                      onClick={() => {
                        setPinMode("none");
                        setPinInput("");
                        setMessage("");
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div style={{ marginTop: '12px' }}>
                  <button className="pin-btn secondary" onClick={() => setPinMode("verify")}>
                    Lock App
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div>
              <div className="setting-item">
                <div>
                  <div className="setting-label">PIN Lock</div>
                  <div className="setting-description">No PIN set</div>
                </div>
              </div>
              {pinMode === "set" ? (
                <div className="pin-section">
                  <input
                    type="password"
                    maxLength={4}
                    placeholder="Enter 4-digit PIN"
                    value={pinInput}
                    onChange={(e) => setPinInput(e.target.value.replace(/\D/g, ""))}
                    className="pin-input"
                  />
                  <input
                    type="password"
                    maxLength={4}
                    placeholder="Confirm PIN"
                    value={confirmPin}
                    onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, ""))}
                    className="pin-input"
                  />
                  <div className="pin-buttons">
                    <button className="pin-btn" onClick={handleSetPIN}>
                      Set PIN
                    </button>
                    <button
                      className="pin-btn secondary"
                      onClick={() => {
                        setPinMode("none");
                        setPinInput("");
                        setConfirmPin("");
                        setMessage("");
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div style={{ marginTop: '12px' }}>
                  <button className="pin-btn" onClick={() => setPinMode("set")}>
                    Set PIN
                  </button>
                </div>
              )}
            </div>
          )}
          {message && (
            <div className={`status-message ${message.includes("success") || message.includes("verified") ? "success" : "error"}`}>
              {message}
            </div>
          )}
        </div>

        {/* About */}
        <div className="settings-group">
          <div className="group-title">ℹ️ About</div>
          <div className="setting-item" style={{ borderBottom: 'none' }}>
            <div>
              <div className="setting-label">DRAVIS - Dynamic Reasoning AI for Virtual Intelligent Study</div>
              <div className="setting-description">Version 1.0.0</div>
              <div className="setting-description">100% Offline AI Study Assistant</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
