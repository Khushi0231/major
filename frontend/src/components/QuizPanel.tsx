import { useState } from "react";
import { generateQuiz } from "../utils/api";
import './QuizPanel.css';

interface QuizQuestion {
  type: string;
  question: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
}

export default function QuizPanel() {
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">("medium");
  const [quizType, setQuizType] = useState<"simple" | "advanced">("simple");
  const [useDocuments, setUseDocuments] = useState(false);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: string }>({});

  async function handleGenerate() {
    if (!topic.trim()) return;

    setLoading(true);
    setQuestions([]);
    setSelectedAnswers({});

    try {
      const result = await generateQuiz(
        topic,
        difficulty,
        quizType,
        useDocuments
      );

      if (result?.questions?.length > 0) {
        setQuestions(result.questions);
      } else {
        setQuestions([]);
      }
    } catch (error) {
      console.error("Quiz generation error:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="quiz-panel">
      {/* Generator Form */}
      <div className="quiz-header">
        <div className="quiz-title">Generate Quiz</div>
        <div className="quiz-controls">
          <input
            placeholder="Enter topic..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
            className="quiz-input"
          />
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value as any)}
            className="quiz-input"
            style={{ flex: 'none', width: 'auto' }}
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
          <select
            value={quizType}
            onChange={(e) => setQuizType(e.target.value as any)}
            className="quiz-input"
            style={{ flex: 'none', width: 'auto' }}
          >
            <option value="simple">Simple</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '12px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', cursor: 'pointer', color: 'var(--text-secondary)' }}>
            <input
              type="checkbox"
              checked={useDocuments}
              onChange={(e) => setUseDocuments(e.target.checked)}
            />
            Use documents
          </label>
          <button
            onClick={handleGenerate}
            disabled={loading || !topic.trim()}
            className="generate-btn"
          >
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="loading-spinner"></span>
                Generating...
              </span>
            ) : "Generate Quiz"}
          </button>
        </div>
      </div>

      {/* Questions */}
      <div className="quiz-content">
        {questions.length === 0 && !loading ? (
          <div className="quiz-empty">
            <div className="empty-icon">📝</div>
            <p>Enter a topic and generate a quiz</p>
          </div>
        ) : (
          <div className="quiz-questions">
            {questions.map((q, idx) => (
              <div key={idx} className="question-card">
                <div className="question-text">
                  <span style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: 'var(--accent)',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    marginRight: '10px',
                    flexShrink: 0
                  }}>
                    {idx + 1}
                  </span>
                  {q.question}
                </div>
                {q.type === "mcq" || q.type === "true_false" ? (
                  <div className="question-options">
                    {q.options?.map((option, optIdx) => (
                      <div
                        key={optIdx}
                        className={`option ${selectedAnswers[idx] === option ? "selected" : ""}`}
                        onClick={() => setSelectedAnswers(prev => ({ ...prev, [idx]: option }))}
                      >
                        <input
                          type="radio"
                          name={`q-${idx}`}
                          value={option}
                          checked={selectedAnswers[idx] === option}
                          onChange={() => setSelectedAnswers(prev => ({ ...prev, [idx]: option }))}
                          style={{ marginRight: '10px' }}
                        />
                        {option}
                      </div>
                    ))}
                  </div>
                ) : (
                  <textarea
                    placeholder="Your answer..."
                    className="quiz-input"
                    rows={3}
                    style={{ width: '100%', resize: 'vertical', marginTop: '8px' }}
                    value={selectedAnswers[idx] || ""}
                    onChange={(e) => setSelectedAnswers(prev => ({ ...prev, [idx]: e.target.value }))}
                  />
                )}
                {selectedAnswers[idx] && (
                  <div style={{
                    marginTop: '12px',
                    padding: '12px',
                    background: 'var(--bg-primary)',
                    borderRadius: '6px',
                    border: '1px solid var(--border)'
                  }}>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--success)', marginBottom: '4px' }}>
                      ✓ Answer: {q.correct_answer}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{q.explanation}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
