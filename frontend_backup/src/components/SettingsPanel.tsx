import React, { useState, useEffect } from "react";
import { setPIN, verifyPIN, checkPINExists } from "../utils/api";

export default function SettingsPanel({
  theme,
  setTheme
}: {
  theme: "dark" | "light";
  setTheme: (t: "dark" | "light") => void;
}) {
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
      const result = await setPIN(pinInput);
      if (result.success) {
        setMessage("PIN set successfully!");
        setPinInput("");
        setConfirmPin("");
        setPinExists(true);
        setPinMode("none");
      } else {
        setMessage("Failed to set PIN");
      }
    } catch (error) {
      setMessage("Error setting PIN");
    }
  };

  const handleVerifyPIN = async () => {
    if (pinInput.length !== 4 || !/^\d{4}$/.test(pinInput)) {
      setMessage("PIN must be exactly 4 digits");
      return;
    }

    try {
      const result = await verifyPIN(pinInput);
      if (result.verified) {
        setMessage("PIN verified!");
        setPinInput("");
        setPinMode("none");
      } else {
        setMessage("Incorrect PIN");
        setPinInput("");
      }
    } catch (error) {
      setMessage("Error verifying PIN");
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      {/* Theme Settings */}
      <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Appearance</h3>
        <div className="flex gap-3">
          <button
            className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
              theme === "dark" ? "bg-blue-600 text-white" : "bg-gray-800/50 text-gray-400 hover:bg-gray-800"
            }`}
            onClick={() => setTheme("dark")}
          >
            🌙 Dark
          </button>
          <button
            className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
              theme === "light" ? "bg-blue-600 text-white" : "bg-gray-800/50 text-gray-400 hover:bg-gray-800"
            }`}
            onClick={() => setTheme("light")}
          >
            ☀️ Light
          </button>
        </div>
      </div>

      {/* PIN Settings */}
      <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Security</h3>
        {pinExists ? (
          <div className="space-y-3">
            <p className="text-sm text-gray-400">PIN is set</p>
            {pinMode === "verify" ? (
              <div className="space-y-3">
                <input
                  type="password"
                  maxLength={4}
                  placeholder="Enter 4-digit PIN"
                  value={pinInput}
                  onChange={(e) => setPinInput(e.target.value.replace(/\D/g, ""))}
                  className="w-full bg-gray-800/50 border border-gray-700/50 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex gap-2">
                  <button
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    onClick={handleVerifyPIN}
                  >
                    Verify
                  </button>
                  <button
                    className="px-4 py-2 bg-gray-800/50 hover:bg-gray-800 text-white rounded-lg transition-colors"
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
              <button
                className="px-4 py-2 bg-gray-800/50 hover:bg-gray-800 text-white rounded-lg transition-colors"
                onClick={() => setPinMode("verify")}
              >
                Lock App
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-gray-400">No PIN set</p>
            {pinMode === "set" ? (
              <div className="space-y-3">
                <input
                  type="password"
                  maxLength={4}
                  placeholder="Enter 4-digit PIN"
                  value={pinInput}
                  onChange={(e) => setPinInput(e.target.value.replace(/\D/g, ""))}
                  className="w-full bg-gray-800/50 border border-gray-700/50 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="password"
                  maxLength={4}
                  placeholder="Confirm PIN"
                  value={confirmPin}
                  onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, ""))}
                  className="w-full bg-gray-800/50 border border-gray-700/50 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex gap-2">
                  <button
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    onClick={handleSetPIN}
                  >
                    Set PIN
                  </button>
                  <button
                    className="px-4 py-2 bg-gray-800/50 hover:bg-gray-800 text-white rounded-lg transition-colors"
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
              <button
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                onClick={() => setPinMode("set")}
              >
                Set PIN
              </button>
            )}
          </div>
        )}
        {message && (
          <div className={`mt-3 text-sm ${message.includes("success") || message.includes("verified") ? "text-green-400" : "text-red-400"}`}>
            {message}
          </div>
        )}
      </div>

      {/* About */}
      <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-3">About</h3>
        <div className="text-sm text-gray-400 space-y-1">
          <p>DRAVIS - Dynamic Reasoning AI for Virtual Intelligent Study</p>
          <p>Version 1.0.0</p>
          <p>100% Offline AI Study Assistant</p>
        </div>
      </div>
    </div>
  );
}
