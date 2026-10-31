"""
AI financial advisor engine.
Supports OpenAI GPT-4o and Anthropic Claude via a unified interface.
Builds context-rich prompts from the user's live financial data.
"""

import json
from typing import Any, Dict, List, Optional

from config.finance_config import AI_SYSTEM_PROMPT
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger("ai_advisor")


# ── Provider-agnostic message type ───────────────────────────────────────────
Message = Dict[str, str]   # {"role": "user"|"assistant", "content": "..."}


class AIAdvisor:
    """
    Unified AI advisor that wraps both OpenAI and Anthropic APIs.
    Financial context is injected into every conversation automatically.
    """

    def __init__(self) -> None:
        self.provider = settings.AI_PROVIDER
        self._openai_client: Optional[Any] = None
        self._anthropic_client: Optional[Any] = None
        self._initialise_client()

    def _initialise_client(self) -> None:
        """Lazy-initialise the chosen AI provider client."""
        try:
            if self.provider == "openai" and settings.OPENAI_API_KEY:
                from openai import AsyncOpenAI
                self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialised (model: %s)", settings.AI_MODEL_OPENAI)
            elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
                import anthropic
                self._anthropic_client = anthropic.AsyncAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY
                )
                logger.info("Anthropic client initialised (model: %s)", settings.AI_MODEL_ANTHROPIC)
            else:
                logger.warning("No AI provider configured — AI features will be disabled.")
        except ImportError as exc:
            logger.error("AI library not installed: %s", exc)

    def build_financial_context(self, user_data: Dict[str, Any]) -> str:
        """
        Build a structured financial context block to inject into the system prompt.

        Args:
            user_data: Dictionary containing expenses, incomes, loans, budgets.

        Returns:
            Formatted string injected before the conversation history.
        """
        ctx_parts: List[str] = ["=== USER FINANCIAL CONTEXT ===\n"]

        # ── Monthly Summary ───────────────────────────────────────────────
        if "summary" in user_data:
            s = user_data["summary"]
            ctx_parts.append(
                f"Monthly Income: ₹{s.get('total_income', 0):,.0f}\n"
                f"Monthly Expenses: ₹{s.get('total_expenses', 0):,.0f}\n"
                f"Net Savings: ₹{s.get('net_savings', 0):,.0f}\n"
                f"Savings Rate: {s.get('savings_rate', 0):.1f}%\n"
            )

        # ── Active Loans ──────────────────────────────────────────────────
        if "loans" in user_data and user_data["loans"]:
            ctx_parts.append("\nActive Loans:\n")
            total_emi = 0.0
            for loan in user_data["loans"]:
                ctx_parts.append(
                    f"  • {loan['loan_name']} ({loan['loan_type']}) — "
                    f"Outstanding: ₹{loan['outstanding_amount']:,.0f}, "
                    f"EMI: ₹{loan['emi_amount']:,.0f}/month, "
                    f"Rate: {loan['annual_interest_rate']}%, "
                    f"Remaining: {loan.get('total_emis_remaining', 'N/A')} EMIs\n"
                )
                total_emi += loan.get("emi_amount", 0)
            ctx_parts.append(f"  Total Monthly EMI Burden: ₹{total_emi:,.0f}\n")

        # ── Top Expense Categories ────────────────────────────────────────
        if "top_categories" in user_data:
            ctx_parts.append("\nTop Expense Categories (this month):\n")
            for cat, amount in user_data["top_categories"].items():
                ctx_parts.append(f"  • {cat}: ₹{amount:,.0f}\n")

        # ── FOIR ──────────────────────────────────────────────────────────
        if "foir" in user_data:
            ctx_parts.append(f"\nFOIR (Debt-to-Income): {user_data['foir']:.1f}%\n")
            if user_data["foir"] > 50:
                ctx_parts.append("⚠ FOIR exceeds 50% — high debt burden, loan eligibility may be impacted.\n")

        ctx_parts.append("=== END CONTEXT ===\n")
        return "".join(ctx_parts)

    async def chat(
        self,
        messages: List[Message],
        user_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send conversation to AI provider and return response text.

        Args:
            messages:  Full conversation history (role + content pairs).
            user_data: Live financial data to inject as context.

        Returns:
            AI response string.

        Raises:
            RuntimeError: If no AI provider is configured.
        """
        if not self._openai_client and not self._anthropic_client:
            return (
                "AI advisor is not configured. "
                "Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file."
            )

        # ── Prepend financial context to system prompt ────────────────────
        system = AI_SYSTEM_PROMPT
        if user_data:
            system = self.build_financial_context(user_data) + "\n\n" + system

        try:
            if self.provider == "openai" and self._openai_client:
                return await self._chat_openai(messages, system)
            else:
                return await self._chat_anthropic(messages, system)
        except Exception as exc:
            logger.error("AI chat error: %s", exc, exc_info=True)
            return f"I encountered an error processing your request. Please try again. ({type(exc).__name__})"

    async def _chat_openai(self, messages: List[Message], system: str) -> str:
        """Call OpenAI chat completions endpoint."""
        full_messages = [{"role": "system", "content": system}] + messages

        response = await self._openai_client.chat.completions.create(
            model=settings.AI_MODEL_OPENAI,
            messages=full_messages,
            max_tokens=settings.AI_MAX_TOKENS,
            temperature=settings.AI_TEMPERATURE,
        )
        return response.choices[0].message.content.strip()

    async def _chat_anthropic(self, messages: List[Message], system: str) -> str:
        """Call Anthropic Messages endpoint."""
        response = await self._anthropic_client.messages.create(
            model=settings.AI_MODEL_ANTHROPIC,
            max_tokens=settings.AI_MAX_TOKENS,
            system=system,
            messages=messages,
        )
        return response.content[0].text.strip()

    async def generate_financial_insight(
        self, user_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Auto-generate dashboard insights without user prompting.

        Returns:
            Dict with keys: health_score, summary, top_concern, top_action.
        """
        prompt = (
            "Based on the financial context provided, give me:\n"
            "1. A financial health score out of 100 with one line reason.\n"
            "2. A 2-sentence overall summary.\n"
            "3. The single biggest financial concern.\n"
            "4. The single most impactful action to take this month.\n"
            'Respond ONLY as JSON: {"health_score": int, "score_reason": str, '
            '"summary": str, "top_concern": str, "top_action": str}'
        )

        raw = await self.chat([{"role": "user", "content": prompt}], user_data)

        try:
            # Strip markdown fences if present
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)
        except Exception:
            return {
                "health_score": 0,
                "score_reason": "Unable to compute",
                "summary": raw,
                "top_concern": "Data analysis pending",
                "top_action": "Add your transactions to get insights",
            }


# Module-level singleton
advisor = AIAdvisor()