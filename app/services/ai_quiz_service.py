import json
from google import genai
from flask import current_app


class AIQuizService:
    """Service that calls the Gemini API to generate structured quiz data."""

    @staticmethod
    def generate_quiz(topic, description='', num_questions=10, difficulty='medium'):
        """
        Generate a quiz via Google Gemini.
        Returns a dict with 'title', 'description', and 'questions' list,
        or raises an exception on failure.
        """
        api_key = current_app.config.get('GEMINI_API_KEY', '')
        if not api_key:
            raise ValueError('Gemini API key is not configured.')

        client = genai.Client(api_key=api_key)

        prompt = f"""You are an expert quiz generator.

Generate a quiz in STRICT JSON format.

Structure:

{{
  "title": "A short engaging title for the quiz",
  "description": "A one‑line description",
  "questions": [
    {{
      "question": "The question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "Brief explanation of correct answer"
    }}
  ]
}}

Rules:
- Exactly {num_questions} questions
- Difficulty: {difficulty}
- Topic: {topic}
- Additional context: {description or 'None provided'}
- All questions must be multiple choice with exactly 4 options
- correct_index must be 0, 1, 2, or 3
- Return ONLY valid JSON — no markdown, no code fences, no commentary
"""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        raw = response.text.strip()

        # Strip markdown code fences if Gemini wraps them
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1]  # remove first line
        if raw.endswith('```'):
            raw = raw.rsplit('```', 1)[0]
        raw = raw.strip()

        data = json.loads(raw)

        # Validate structure
        if 'questions' not in data or not isinstance(data['questions'], list):
            raise ValueError('Invalid quiz structure returned by AI.')

        if len(data['questions']) == 0:
            raise ValueError('AI returned zero questions.')

        for i, q in enumerate(data['questions']):
            if not all(k in q for k in ('question', 'options', 'correct_index')):
                raise ValueError(f'Question {i + 1} is missing required fields.')
            if len(q['options']) != 4:
                raise ValueError(f'Question {i + 1} must have exactly 4 options.')
            if q['correct_index'] not in (0, 1, 2, 3):
                raise ValueError(f'Question {i + 1} has invalid correct_index.')

        return data
