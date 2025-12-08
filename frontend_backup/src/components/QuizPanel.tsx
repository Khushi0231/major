import React, { useState } from "react";
import { generateQuiz } from "../utils/api";

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
      const result = await generateQuiz({
        topic,
        num_questions: 5,
        difficulty,
        quiz_type: quizType,
        use_documents: useDocuments
      });

      if (result.success && result.quiz?.questions) {
        setQuestions(result.quiz.questions);
      }
    } catch (error) {
      console.error("Quiz generation error:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Generator Form */}
      <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Generate Quiz</h3>
        <div className="space-y-4">
          <input
            placeholder="Enter topic..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
            className="w-full bg-gray-800/50 border border-gray-700/50 text-white px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="grid grid-cols-2 gap-4">
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value as any)}
              className="bg-gray-800/50 border border-gray-700/50 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <select
              value={quizType}
              onChange={(e) => setQuizType(e.target.value as any)}
              className="bg-gray-800/50 border border-gray-700/50 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="simple">Simple</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={useDocuments}
              onChange={(e) => setUseDocuments(e.target.checked)}
              className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-500"
            />
            Use documents
          </label>
          <button
            onClick={handleGenerate}
            disabled={loading || !topic.trim()}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? "Generating..." : "Generate Quiz"}
          </button>
        </div>
      </div>

      {/* Questions */}
      {questions.length > 0 && (
        <div className="space-y-4">
          {questions.map((q, idx) => (
            <div key={idx} className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6">
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                  {idx + 1}
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-white mb-3">{q.question}</div>
                  {q.type === "mcq" || q.type === "true_false" ? (
                    <div className="space-y-2">
                      {q.options?.map((option, optIdx) => (
                        <label
                          key={optIdx}
                          className={`block p-3 rounded-lg cursor-pointer transition-all ${
                            selectedAnswers[idx] === option
                              ? "bg-blue-600/20 border border-blue-500"
                              : "bg-gray-800/50 border border-gray-700/50 hover:bg-gray-800"
                          }`}
                        >
                          <input
                            type="radio"
                            name={`q-${idx}`}
                            value={option}
                            checked={selectedAnswers[idx] === option}
                            onChange={() => setSelectedAnswers(prev => ({ ...prev, [idx]: option }))}
                            className="mr-3"
                          />
                          {option}
                        </label>
                      ))}
                    </div>
                  ) : (
                    <textarea
                      placeholder="Your answer..."
                      className="w-full bg-gray-800/50 border border-gray-700/50 text-white p-3 rounded-lg"
                      rows={3}
                      value={selectedAnswers[idx] || ""}
                      onChange={(e) => setSelectedAnswers(prev => ({ ...prev, [idx]: e.target.value }))}
                    />
                  )}
                  {selectedAnswers[idx] && (
                    <div className="mt-4 p-4 bg-gray-900/50 rounded-lg border border-gray-700/50">
                      <div className="text-sm font-semibold text-green-400 mb-1">
                        ✓ Answer: {q.correct_answer}
                      </div>
                      <div className="text-xs text-gray-400">{q.explanation}</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
