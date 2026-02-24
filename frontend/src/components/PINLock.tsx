import React, { useState, useEffect } from "react";
import { verifyPIN, checkPINExists } from "../utils/api";
import './PINLock.css';

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
        onUnlock();
      } else {
        setChecking(false);
      }
    } catch (error) {
      console.error("Failed to check PIN (backend may not be running):", error);
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
      <div className="pin-lock-overlay">
        <div className="pin-lock-loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="pin-lock-overlay">
      <div className="pin-lock-card">
        <div className="pin-lock-header">
          <div className="pin-lock-title">DRAVIS</div>
          <div className="pin-lock-subtitle">Enter 4-digit PIN to unlock</div>
        </div>

        <form onSubmit={handleSubmit} className="pin-lock-form">
          <div className="pin-lock-inputs">
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
                className="pin-lock-digit"
                autoFocus={i === 0}
              />
            ))}
          </div>

          {error && (
            <div className="pin-lock-error">{error}</div>
          )}

          <button
            type="submit"
            className="pin-lock-submit"
            disabled={pin.length !== 4}
          >
            Unlock
          </button>
        </form>
      </div>
    </div>
  );
}
