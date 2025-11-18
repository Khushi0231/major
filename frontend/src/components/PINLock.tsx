import React, { useState, useEffect } from "react";
import { verifyPIN, checkPINExists } from "../utils/api";

export default function PINLock({ onUnlock }: { onUnlock: () => void }) {
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    checkPinStatus();
  }, []);

  const checkPinStatus = async () => {
    try {
      const result = await checkPINExists();
      if (!result.exists) {
        // No PIN set, unlock immediately
        onUnlock();
      } else {
        setChecking(false);
      }
    } catch (error) {
      console.error("Failed to check PIN (backend may not be running):", error);
      // If backend is not available, assume no PIN and unlock
      // This allows the app to work even if backend is starting
      onUnlock();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (pin.length !== 4) {
      setError("PIN must be 4 digits");
      return;
    }

    try {
      const result = await verifyPIN(pin);
      if (result.verified) {
        onUnlock();
      } else {
        setError("Incorrect PIN");
        setPin("");
      }
    } catch (error) {
      setError("Error verifying PIN");
      setPin("");
    }
  };

  if (checking) {
    return (
      <div className="fixed inset-0 bg-gray-950 flex items-center justify-center">
        <div className="text-pink-400 text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-950 flex items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-xl shadow-lg max-w-md w-full">
        <div className="text-center mb-6">
          <div className="text-3xl font-bold text-pink-400 mb-2">DRAVIS</div>
          <div className="text-gray-400">Enter 4-digit PIN to unlock</div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex justify-center gap-2">
            {[0, 1, 2, 3].map((i) => (
              <input
                key={i}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={pin[i] || ""}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, "");
                  if (value) {
                    const newPin = pin.slice(0, i) + value + pin.slice(i + 1);
                    setPin(newPin.slice(0, 4));
                    setError("");
                    // Auto-focus next input
                    if (i < 3 && value) {
                      const nextInput = document.querySelector(
                        `input[data-pin-index="${i + 1}"]`
                      ) as HTMLInputElement;
                      nextInput?.focus();
                    }
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Backspace" && !pin[i] && i > 0) {
                    const prevInput = document.querySelector(
                      `input[data-pin-index="${i - 1}"]`
                    ) as HTMLInputElement;
                    prevInput?.focus();
                  }
                }}
                data-pin-index={i}
                className="w-12 h-12 text-center text-2xl font-bold bg-gray-700 text-white rounded border-2 border-gray-600 focus:border-pink-500 focus:outline-none"
                autoFocus={i === 0}
              />
            ))}
          </div>

          {error && (
            <div className="text-center text-red-400 text-sm">{error}</div>
          )}

          <button
            type="submit"
            className="w-full bg-pink-700 hover:bg-pink-600 text-white py-3 rounded-lg font-semibold transition"
            disabled={pin.length !== 4}
          >
            Unlock
          </button>
        </form>
      </div>
    </div>
  );
}

