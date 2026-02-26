import React, { useState, useEffect, useRef } from "react";
import './PINLock.css';

interface PINLockProps {
  onUnlock: () => void;
}

export default function PINLock({ onUnlock }: PINLockProps) {
  const [mode, setMode] = useState<"loading" | "set" | "verify">("loading");
  const [pin, setPin] = useState(["", "", "", ""]);
  const [confirmPin, setConfirmPin] = useState(["", "", "", ""]);
  const [step, setStep] = useState<"enter" | "confirm">("enter");
  const [error, setError] = useState("");
  const [shaking, setShaking] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    const savedPin = localStorage.getItem("dravis_pin");
    setMode(savedPin ? "verify" : "set");
  }, []);

  const focusInput = (idx: number) => {
    setTimeout(() => inputRefs.current[idx]?.focus(), 50);
  };

  const handleDigit = (index: number, value: string, target: "pin" | "confirm") => {
    const digit = value.replace(/\D/g, "").slice(-1);
    const setter = target === "pin" ? setPin : setConfirmPin;
    const current = target === "pin" ? [...pin] : [...confirmPin];
    current[index] = digit;
    setter(current);
    setError("");

    if (digit && index < 3) {
      focusInput(index + 1);
    }

    // Auto-submit on last digit
    if (digit && index === 3) {
      const fullPin = current.join("");
      if (fullPin.length === 4) {
        if (mode === "verify") {
          verifyPin(fullPin);
        } else if (step === "enter") {
          // Move to confirm step
          setTimeout(() => {
            setStep("confirm");
            setConfirmPin(["", "", "", ""]);
            focusInput(0);
          }, 200);
        } else {
          // Confirm step — check match
          const originalPin = pin.join("");
          if (fullPin === originalPin) {
            localStorage.setItem("dravis_pin", btoa(fullPin));
            onUnlock();
          } else {
            triggerError("PINs don't match — try again");
            setStep("enter");
            setPin(["", "", "", ""]);
            setConfirmPin(["", "", "", ""]);
            focusInput(0);
          }
        }
      }
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && index > 0) {
      const target = mode === "set" && step === "confirm" ? "confirm" : "pin";
      const current = target === "pin" ? [...pin] : [...confirmPin];
      if (!current[index]) {
        focusInput(index - 1);
      }
    }
  };

  const verifyPin = (entered: string) => {
    const saved = localStorage.getItem("dravis_pin");
    if (saved && btoa(entered) === saved) {
      onUnlock();
    } else {
      triggerError("Wrong PIN");
      setPin(["", "", "", ""]);
      focusInput(0);
    }
  };

  const triggerError = (msg: string) => {
    setError(msg);
    setShaking(true);
    setTimeout(() => setShaking(false), 500);
  };

  if (mode === "loading") {
    return (
      <div className="pin-screen">
        <div className="pin-loading-spinner" />
      </div>
    );
  }

  const isConfirmStep = mode === "set" && step === "confirm";
  const currentPin = isConfirmStep ? confirmPin : pin;

  return (
    <div className="pin-screen">
      <div className="pin-card">
        <div className="pin-logo">D</div>
        <h1 className="pin-title">DRAVIS</h1>
        <p className="pin-subtitle">
          {mode === "set"
            ? step === "enter"
              ? "Create a 4-digit PIN to secure your sessions"
              : "Re-enter PIN to confirm"
            : "Enter your PIN to unlock"
          }
        </p>

        <div className={`pin-inputs ${shaking ? "shake" : ""}`}>
          {[0, 1, 2, 3].map((i) => (
            <input
              key={`${step}-${i}`}
              ref={(el) => { inputRefs.current[i] = el; }}
              type="password"
              inputMode="numeric"
              maxLength={1}
              value={currentPin[i]}
              onChange={(e) => handleDigit(i, e.target.value, isConfirmStep ? "confirm" : "pin")}
              onKeyDown={(e) => handleKeyDown(i, e)}
              className="pin-digit"
              autoFocus={i === 0}
            />
          ))}
        </div>

        {error && <div className="pin-error">{error}</div>}

        <div className="pin-dots">
          {currentPin.map((d, i) => (
            <span key={i} className={`pin-dot ${d ? "filled" : ""}`} />
          ))}
        </div>

        {mode === "set" && step === "enter" && (
          <p className="pin-hint">This PIN protects your chat history</p>
        )}
      </div>
    </div>
  );
}
