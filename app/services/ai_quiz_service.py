"""
Gemini Multi-Model AI Quiz Service
───────────────────────────────────
Supports round-robin model rotation, automatic fallback on retryable errors,
per-model cooldown, structured logging, and DB usage tracking.
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta

from google import genai
from flask import current_app

logger = logging.getLogger(__name__)


# ── Custom Exceptions ────────────────────────────────────────────────

class RetryableError(Exception):
    """Error that should trigger a fallback to the next model."""
    pass


class NonRetryableError(Exception):
    """Error that should stop the retry loop immediately."""
    pass


# ── Round-Robin Model Selector ───────────────────────────────────────

class ModelSelector:
    """Thread-safe round-robin model selector with cooldown tracking."""

    def __init__(self):
        self._index = 0
        self._lock = threading.Lock()
        # model_name → datetime when cooldown expires
        self._cooldowns: dict[str, datetime] = {}

    def next_model(self, models: list[str]) -> str:
        """Return the next model in round-robin order."""
        with self._lock:
            model = models[self._index % len(models)]
            self._index = (self._index + 1) % len(models)
            return model

    def mark_cooldown(self, model_name: str, minutes: int) -> None:
        with self._lock:
            self._cooldowns[model_name] = datetime.now() + timedelta(minutes=minutes)
            logger.warning('Model %s cooled down for %d minutes', model_name, minutes)

    def is_available(self, model_name: str) -> bool:
        with self._lock:
            expires = self._cooldowns.get(model_name)
            if expires is None:
                return True
            if datetime.now() >= expires:
                del self._cooldowns[model_name]
                return True
            return False

    def get_available_models(self, models: list[str]) -> list[str]:
        return [m for m in models if self.is_available(m)]

    def get_cooldowns(self) -> dict[str, datetime]:
        with self._lock:
            now = datetime.now()
            return {k: v for k, v in self._cooldowns.items() if v > now}


# Module-level singleton — survives across requests
_selector = ModelSelector()


# ── AI Quiz Service ──────────────────────────────────────────────────

class AIQuizService:
    """Service that generates quizzes via the Gemini API with multi-model fallback."""

    # ── Public entry point (same signature as before) ────────────

    @staticmethod
    def generate_quiz(topic, description='', num_questions=10, difficulty='medium'):
        """
        Build the prompt, then delegate to the fallback engine.
        Returns a dict with 'title', 'description', 'questions', and 'model_used'.
        """
        api_key = current_app.config.get('GEMINI_API_KEY', '')
        if not api_key:
            raise ValueError('Gemini API key is not configured.')

        prompt = AIQuizService._build_prompt(topic, description, num_questions, difficulty)

        models = current_app.config.get('GEMINI_MODELS', ['gemini-2.5-flash'])
        fallback = current_app.config.get('GEMINI_FALLBACK_ENABLED', True)
        max_retries = current_app.config.get('GEMINI_MAX_RETRIES', 3)
        timeout = current_app.config.get('GEMINI_TIMEOUT', 60)
        cooldown_min = current_app.config.get('GEMINI_COOLDOWN_MINUTES', 5)

        if fallback:
            return AIQuizService._generate_with_fallback(
                api_key, prompt, models, max_retries, timeout, cooldown_min
            )
        else:
            # Single model, no fallback
            model = _selector.next_model(models)
            return AIQuizService._generate_with_model(api_key, model, prompt, timeout)

    # ── Fallback engine ──────────────────────────────────────────

    @staticmethod
    def _generate_with_fallback(api_key, prompt, models, max_retries, timeout, cooldown_min):
        """
        Iterate through available models with retry logic.
        Retryable errors trigger fallback to the next model.
        Non-retryable errors stop the loop immediately.
        """
        attempts = 0
        errors = []

        # Build an ordered candidate list starting from the round-robin position
        available = _selector.get_available_models(models)
        if not available:
            # All models cooled down — try anyway with full list
            logger.warning('All models are in cooldown — trying full list.')
            available = list(models)

        for model in available:
            if attempts >= max_retries:
                break

            attempts += 1
            logger.info('[Attempt %d/%d] Trying model: %s', attempts, max_retries, model)

            try:
                result = AIQuizService._generate_with_model(api_key, model, prompt, timeout)

                # Success — record to DB
                AIQuizService._record_usage(model, success=True)
                logger.info('✅ Success with model: %s', model)

                result['model_used'] = model
                return result

            except RetryableError as e:
                logger.warning('⚠️  Retryable error on %s: %s', model, e)
                errors.append(f'{model}: {e}')
                _selector.mark_cooldown(model, cooldown_min)
                AIQuizService._record_usage(model, success=False)
                continue

            except NonRetryableError as e:
                logger.error('🛑 Non-retryable error on %s: %s', model, e)
                errors.append(f'{model}: {e}')
                AIQuizService._record_usage(model, success=False)
                break

            except Exception as e:
                logger.error('❌ Unexpected error on %s: %s', model, e)
                errors.append(f'{model}: {e}')
                AIQuizService._record_usage(model, success=False)
                continue

        error_details = '; '.join(errors)
        raise RuntimeError(
            f'All AI models failed after {attempts} attempt(s). Errors: {error_details}'
        )

    # ── Single-model call ────────────────────────────────────────

    @staticmethod
    def _generate_with_model(api_key, model_name, prompt, timeout):
        """
        Call a specific Gemini model, parse JSON, validate structure.
        Raises RetryableError or NonRetryableError depending on failure type.
        """
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
        except Exception as e:
            AIQuizService._categorize_api_error(e)

        # Parse and validate
        raw = response.text.strip()
        raw = AIQuizService._strip_code_fences(raw)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RetryableError(f'Invalid JSON from {model_name}: {e}')

        AIQuizService._validate_quiz(data)
        return data

    # ── Error categorisation ─────────────────────────────────────

    @staticmethod
    def _categorize_api_error(error):
        """Inspect an API exception and raise the correct wrapper."""
        err_str = str(error).lower()

        # Retryable status codes / keywords
        retryable_signals = ['429', 'rate limit', '503', 'overloaded', 'timeout', 'deadline']
        for signal in retryable_signals:
            if signal in err_str:
                raise RetryableError(str(error)) from error

        # Non-retryable
        non_retryable_signals = ['401', '403', 'permission', 'invalid api key', 'forbidden']
        for signal in non_retryable_signals:
            if signal in err_str:
                raise NonRetryableError(str(error)) from error

        # Default to retryable (best-effort)
        raise RetryableError(str(error)) from error

    # ── Prompt builder ───────────────────────────────────────────

    @staticmethod
    def _build_prompt(topic, description, num_questions, difficulty):
        return f"""You are an expert quiz generator.

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

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _strip_code_fences(raw: str) -> str:
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1]
        if raw.endswith('```'):
            raw = raw.rsplit('```', 1)[0]
        return raw.strip()

    @staticmethod
    def _validate_quiz(data: dict) -> None:
        if 'questions' not in data or not isinstance(data['questions'], list):
            raise RetryableError('Invalid quiz structure returned by AI.')
        if len(data['questions']) == 0:
            raise RetryableError('AI returned zero questions.')

        for i, q in enumerate(data['questions']):
            if not all(k in q for k in ('question', 'options', 'correct_index')):
                raise RetryableError(f'Question {i + 1} is missing required fields.')
            if len(q['options']) != 4:
                raise RetryableError(f'Question {i + 1} must have exactly 4 options.')
            if q['correct_index'] not in (0, 1, 2, 3):
                raise RetryableError(f'Question {i + 1} has invalid correct_index.')

    # ── DB usage tracking ────────────────────────────────────────

    @staticmethod
    def _record_usage(model_name: str, success: bool) -> None:
        """Persist a usage record to AIModelUsage (best-effort, non-blocking)."""
        try:
            from app import db
            from app.models.ai_usage import AIModelUsage
            from datetime import date

            today = date.today()
            record = AIModelUsage.query.filter_by(model_name=model_name, date=today).first()

            if record is None:
                record = AIModelUsage(
                    model_name=model_name,
                    date=today,
                    success_count=0,
                    failure_count=0,
                )
                db.session.add(record)

            if success:
                record.success_count += 1
                record.status = 'active'
            else:
                record.failure_count += 1
                record.last_failure_at = datetime.now()
                record.status = 'degraded'

            db.session.commit()
        except Exception as e:
            logger.warning('Failed to record AI usage: %s', e)
            try:
                from app import db
                db.session.rollback()
            except Exception:
                pass

    # ── Selector access for admin panel ──────────────────────────

    @staticmethod
    def get_cooldowns() -> dict[str, datetime]:
        return _selector.get_cooldowns()
