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
  const [revealed, setRevealed] = useState<{ [key: number]: boolean }>({});

  async function handleGenerate() {
    if (!topic.trim()) return;
    setLoading(true);
    setQuestions([]);
    setSelectedAnswers({});
    setRevealed({});
    try {
      const result = await generateQuiz(topic, difficulty, quizType, useDocuments);
      if (result?.questions?.length > 0) setQuestions(result.questions);
    } catch (err) {
      console.error("Quiz generation error:", err);
    } finally {
      setLoading(false);
    }
  }

  const score = questions.length > 0
    ? questions.filter((q, i) => selectedAnswers[i] === q.correct_answer).length
    : 0;

  return (
    <div className="quiz-panel">
      {/* Generator */}
      <div className="quiz-header">
        <div className="quiz-title">Generate Quiz</div>
        <div className="quiz-form">
          <input
            className="quiz-input"
            placeholder="Enter a topic (e.g. Photosynthesis, World War II)..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
          />
          <div className="quiz-options-row">
            <select className="quiz-select" value={difficulty} onChange={(e) => setDifficulty(e.target.value as any)}>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <select className="quiz-select" value={quizType} onChange={(e) => setQuizType(e.target.value as any)}>
              <option value="simple">MCQ</option>
              <option value="advanced">Short Answer</option>
            </select>
            <label className="quiz-doc-toggle">
              <input type="checkbox" checked={useDocuments} onChange={(e) => setUseDocuments(e.target.checked)} />
              From docs
            </label>
          </div>
          <button className="quiz-generate-btn" onClick={handleGenerate} disabled={loading || !topic.trim()}>
            {loading ? "Generating..." : "Generate"}
          </button>
        </div>
      </div>

      {/* Questions */}
      <div className="quiz-content">
        {loading && (
          <div className="quiz-loading">
            <div className="loading-spinner" />
            <span>Generating questions with AI...</span>
          </div>
        )}

        {questions.length > 0 && (
          <>
            <div className="quiz-score-bar">
              <span>Score: {score}/{questions.length}</span>
              <span>{Math.round((score / questions.length) * 100)}%</span>
            </div>

            <div className="quiz-questions">
              {questions.map((q, idx) => (
                <div key={idx} className="q-card">
                  <div className="q-number">{idx + 1}</div>
                  <div className="q-body">
                    <div className="q-text">{q.question}</div>

                    {(q.type === "mcq" || q.type === "true_false") && q.options ? (
                      <div className="q-options">
                        {q.options.map((opt, optIdx) => {
                          const selected = selectedAnswers[idx] === opt;
                          const isRevealed = revealed[idx];
                          const isCorrect = opt === q.correct_answer;
                          let cls = "q-option";
                          if (selected) cls += " selected";
                          if (isRevealed && isCorrect) cls += " correct";
                          if (isRevealed && selected && !isCorrect) cls += " incorrect";

                          return (
                            <button
                              key={optIdx}
                              className={cls}
                              onClick={() => {
                                setSelectedAnswers(p => ({ ...p, [idx]: opt }));
                                setRevealed(p => ({ ...p, [idx]: true }));
                              }}
                              disabled={isRevealed}
                            >
                              <span className="q-option-letter">{String.fromCharCode(65 + optIdx)}</span>
                              {opt}
                            </button>
                          );
                        })}
                      </div>
                    ) : (
                      <textarea
                        className="q-textarea"
                        placeholder="Type your answer..."
                        rows={2}
                        value={selectedAnswers[idx] || ""}
                        onChange={(e) => setSelectedAnswers(p => ({ ...p, [idx]: e.target.value }))}
                      />
                    )}

                    {revealed[idx] && (
                      <div className="q-explanation">
                        <div className="q-answer">Answer: {q.correct_answer}</div>
                        <div className="q-explain-text">{q.explanation}</div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {!loading && questions.length === 0 && (
          <div className="quiz-empty">
            <div className="quiz-empty-icon">🧠</div>
            <div>Enter a topic above to generate a quiz</div>
            <div className="quiz-empty-hint">AI will create questions based on the topic or your uploaded documents</div>
          </div>
        )}
      </div>
    </div>
  );
}
