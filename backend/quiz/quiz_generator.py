"""Quiz generation module"""
import logging
from typing import List, Dict, Optional
from backend.models.llm_manager import LLMManager

logger = logging.getLogger(__name__)


class QuizGenerator:
    def __init__(self, llm_handler: LLMManager = None):
        self.llm = llm_handler or LLMManager()
    
    def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        quiz_type: str = "simple",
        context: Optional[str] = None
    ) -> Dict:
        """
        Generate quiz questions.
        
        Args:
            topic: Topic or subject for quiz
            num_questions: Number of questions (5-10)
            difficulty: easy, medium, or hard
            quiz_type: "simple" (MCQ/True-False) or "advanced" (Fill-in-blank/Short Answer)
            context: Optional document context for RAG-based quizzes
        
        Returns:
            Dictionary with quiz questions, options, answers, explanations
        """
        num_questions = max(5, min(10, num_questions))
        
        if quiz_type == "simple":
            return self._generate_simple_quiz(topic, num_questions, difficulty, context)
        else:
            return self._generate_advanced_quiz(topic, num_questions, difficulty, context)
    
    def _generate_simple_quiz(
        self,
        topic: str,
        num_questions: int,
        difficulty: str,
        context: Optional[str]
    ) -> Dict:
        """Generate simple quiz (MCQ and True/False)"""
        
        context_text = f"\n\nContext from documents:\n{context}" if context else ""
        
        prompt = f"""Generate {num_questions} {difficulty} difficulty quiz questions about: {topic}

Requirements:
- Mix of Multiple Choice Questions (MCQ) and True/False questions
- Each question should have exactly 4 options (A, B, C, D) for MCQ
- For True/False, use options: A) True, B) False
- Provide correct answer (A, B, C, or D)
- Include brief explanation (1-2 sentences)

Format as JSON:
{{
  "questions": [
    {{
      "type": "mcq" or "true_false",
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "A",
      "explanation": "Brief explanation"
    }}
  ]
}}
{context_text}

Return ONLY valid JSON, no additional text."""
        
        response = self.llm.generate(prompt)
        
        # Parse response (basic JSON extraction)
        try:
            import json
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                quiz_data = json.loads(json_str)
                return quiz_data
        except Exception as e:
            logger.error(f"Failed to parse quiz JSON: {e}")
        
        # Fallback: generate simple structure
        return self._generate_fallback_quiz(topic, num_questions)
    
    def _generate_advanced_quiz(
        self,
        topic: str,
        num_questions: int,
        difficulty: str,
        context: Optional[str]
    ) -> Dict:
        """Generate advanced quiz (Fill-in-blank and Short Answer)"""
        
        context_text = f"\n\nContext from documents:\n{context}" if context else ""
        
        prompt = f"""Generate {num_questions} {difficulty} difficulty advanced quiz questions about: {topic}

Requirements:
- Mix of Fill-in-the-blank and Short Answer questions
- For Fill-in-the-blank: Use _____ to indicate blank
- For Short Answer: Ask open-ended questions requiring 2-3 sentence answers
- Provide correct answer or sample answer
- Include brief explanation

Format as JSON:
{{
  "questions": [
    {{
      "type": "fill_blank" or "short_answer",
      "question": "Question text with _____ for blanks",
      "correct_answer": "Correct answer or sample answer",
      "explanation": "Brief explanation"
    }}
  ]
}}
{context_text}

Return ONLY valid JSON, no additional text."""
        
        response = self.llm.generate(prompt)
        
        try:
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                quiz_data = json.loads(json_str)
                return quiz_data
        except Exception as e:
            logger.error(f"Failed to parse advanced quiz JSON: {e}")
        
        return self._generate_fallback_quiz(topic, num_questions, advanced=True)
    
    def _generate_fallback_quiz(self, topic: str, num_questions: int, advanced: bool = False) -> Dict:
        """Generate fallback quiz structure if LLM parsing fails"""
        questions = []
        
        for i in range(num_questions):
            if advanced:
                questions.append({
                    "type": "short_answer" if i % 2 == 0 else "fill_blank",
                    "question": f"Question {i+1} about {topic}?",
                    "correct_answer": f"Sample answer for question {i+1}",
                    "explanation": f"Explanation for question {i+1}"
                })
            else:
                questions.append({
                    "type": "mcq" if i % 2 == 0 else "true_false",
                    "question": f"Question {i+1} about {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "A",
                    "explanation": f"Explanation for question {i+1}"
                })
        
        return {"questions": questions}

