import React, { useState } from "react";

export default function QuizPanel(){
  const [topic, setTopic] = useState("");
  const [diff, setDiff] = useState("easy");
  const [cards, setCards] = useState<{q:string,a:string}[]>([]);

  async function generate(){
    // simple client-side generation placeholder (could call backend later)
    setCards([
      {q:`What is ${topic}?`, a:`Short answer about ${topic}`},
      {q:`Why is ${topic} important?`, a:`Because...`}
    ]);
  }

  return (
    <div className="p-4 bg-white/5 rounded">
      <div style={{fontWeight:700}}>Quiz Generator</div>
      <div className="kv mb-3">Create small quizzes from uploaded docs or topics</div>

      <div className="mb-3">
        <input placeholder="Topic" value={topic} onChange={e=>setTopic(e.target.value)} className="input-box" />
      </div>
      <div className="mb-3">
        <select value={diff} onChange={e=>setDiff(e.target.value)} className="btn small">
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
        <button className="btn small ml-2" onClick={generate}>Generate</button>
      </div>

      <div>
        {cards.map((c,i)=>(
          <div key={i} className="doc-item">
            <div>
              <div style={{fontWeight:700}}>Q: {c.q}</div>
              <div className="kv">A: {c.a}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}