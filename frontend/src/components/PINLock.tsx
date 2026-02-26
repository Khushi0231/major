import React, { useState, useEffect, useRef } from "react";
import { verifyPIN, checkPINExists } from "../utils/api";
import './PINLock.css';

export default function PINLock({ onUnlock }: { onUnlock: () => void }) {
  const [pin, setPin] = useState(["", "", "", ""]);
  const [error, setError] = useState("");
  const [checking, setChecking] = useState(true);
  const [shaking, setShaking] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    checkPinStatus();
  }, []);

  const checkPinStatus = async () => {
    // Check localStorage first (faster)
    const localPin = localStorage.getItem("dravis_pin");
    if (localPin) {
      setChecking(false);
      return;
    }
    try {
      const result = await checkPINExists();
      if (!result.exists) {
        onUnlock(); // No PIN set
      } else {
        setChecking(false);
      }
    } catch {
      // Backend not available, check localStorage
      if (!localPin) onUnlock();
      else setChecking(false);
    }
  };

  const handleDigit = (index: number, value: string) => {
    const digit = value.replace(/\D/g, "").slice(-1);
    const newPin = [...pin];
    newPin[index] = digit;
    setPin(newPin);
    setError("");

    if (digit && index < 3) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all 4 digits entered
    if (digit && index === 3) {
      const fullPin = newPin.join("");
      if (fullPin.length === 4) {
        verifyEnteredPIN(fullPin);
      }
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !pin[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const verifyEnteredPIN = async (enteredPin: string) => {
    // Check localStorage first
    const localPin = localStorage.getItem("dravis_pin");
    if (localPin) {
      if (btoa(enteredPin) === localPin) {
        onUnlock();
        return;
      } else {
        triggerError();
        return;
      }
    }

    try {
      const result = await verifyPIN(enteredPin);
      if (result.verified) {
        onUnlock();
      } else {
        triggerError();
      }
    } catch {
      triggerError();
    }
  };

  const triggerError = () => {
    setError("Incorrect PIN");
    setShaking(true);
    setPin(["", "", "", ""]);
    inputRefs.current[0]?.focus();
    setTimeout(() => setShaking(false), 500);
  };

  if (checking) {
    return (
      <div className="pin-screen">
        <div className="pin-loading-spinner" />
      </div>
    );
  }

  return (
    <div className="pin-screen">
      <div className="pin-card">
        <div className="pin-logo">D</div>
        <h1 className="pin-title">DRAVIS</h1>
        <p className="pin-subtitle">Enter your 4-digit PIN to unlock</p>

        <div className={`pin-inputs ${shaking ? "shake" : ""}`}>
          {pin.map((digit, i) => (
            <input
              key={i}
              ref={(el) => { inputRefs.current[i] = el; }}
              type="password"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleDigit(i, e.target.value)}
              onKeyDown={(e) => handleKeyDown(i, e)}
              className="pin-digit"
              autoFocus={i === 0}
            />
          ))}
        </div>

        {error && <div className="pin-error">{error}</div>}

        <div className="pin-dots">
          {pin.map((d, i) => (
            <span key={i} className={`pin-dot ${d ? "filled" : ""}`} />
          ))}
        </div>
      </div>
    </div>
  );
}
