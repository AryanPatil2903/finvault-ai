"""
AI chat endpoints: start conversation, continue conversation, get history.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user
from api.schemas import AIChatRequest, AIChatResponse
from database.connection import get_db
from database.models import AIConversation, Expense, Income, Loan, User
from src.ai_advisor import advisor

router = APIRouter(prefix="/ai", tags=["AI Advisor"])


async def _get_user_financial_context(
    user: User, db: AsyncSession
) -> Dict[str, Any]:
    """Build financial context dict from live user data for AI injection."""
    # Recent income total (current month)
    from datetime import date
    today = date.today()
    month_start = today.replace(day=1)

    inc_result = await db.execute(
        select(Income).where(Income.user_id == user.id,
                             Income.transaction_date >= month_start)
    )
    total_income = sum(i.amount for i in inc_result.scalars())

    exp_result = await db.execute(
        select(Expense).where(Expense.user_id == user.id,
                              Expense.transaction_date >= month_start)
    )
    expenses = list(exp_result.scalars())
    total_expenses = sum(e.amount for e in expenses)

    loans_result = await db.execute(
        select(Loan).where(Loan.user_id == user.id, Loan.status == "Active")
    )
    active_loans = list(loans_result.scalars())

    from collections import defaultdict
    cat_totals: Dict[str, float] = defaultdict(float)
    for e in expenses:
        cat_totals[e.category] += e.amount
    top_cats = dict(sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)[:5])

    from src.finance import calculate_foir
    total_emi = sum(l.emi_amount for l in active_loans)
    foir = calculate_foir(total_emi, user.monthly_income or total_income)

    return {
        "summary": {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": total_income - total_expenses,
            "savings_rate": round(((total_income - total_expenses) / total_income * 100) if total_income else 0, 2),
        },
        "loans": [
            {
                "loan_name": l.loan_name,
                "loan_type": l.loan_type,
                "outstanding_amount": l.outstanding_amount,
                "emi_amount": l.emi_amount,
                "annual_interest_rate": l.annual_interest_rate,
                "total_emis_remaining": l.total_emis_remaining,
            }
            for l in active_loans
        ],
        "top_categories": top_cats,
        "foir": foir,
    }


@router.post("/chat", response_model=AIChatResponse)
async def chat(
    body: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AIChatResponse:
    """
    Send a message to the AI advisor and receive a financial insight response.
    Maintains full conversation history per session.
    """
    # ── Load or create conversation ───────────────────────────────────────
    conversation = None
    if body.conversation_id:
        result = await db.execute(
            select(AIConversation).where(
                AIConversation.id == body.conversation_id,
                AIConversation.user_id == current_user.id,
            )
        )
        conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = AIConversation(
            user_id=current_user.id,
            title=body.message[:50],
            messages=[],
        )
        db.add(conversation)
        await db.flush()

    # ── Append user message ───────────────────────────────────────────────
    from datetime import datetime, timezone
    messages = list(conversation.messages)
    messages.append({
        "role": "user",
        "content": body.message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # ── Build AI message list (role + content only) ───────────────────────
    ai_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

    # ── Inject financial context if requested ─────────────────────────────
    user_data = None
    if body.include_financial_context:
        user_data = await _get_user_financial_context(current_user, db)

    # ── Get AI response ───────────────────────────────────────────────────
    reply = await advisor.chat(ai_messages, user_data)

    # ── Append assistant response ─────────────────────────────────────────
    messages.append({
        "role": "assistant",
        "content": reply,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    conversation.messages = messages
    await db.flush()

    return AIChatResponse(
        conversation_id=conversation.id,
        reply=reply,
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
    )


@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List all AI conversations for the current user."""
    result = await db.execute(
        select(AIConversation)
        .where(AIConversation.user_id == current_user.id)
        .order_by(AIConversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return [
        {"id": c.id, "title": c.title, "created_at": c.created_at, "message_count": len(c.messages)}
        for c in conversations
    ]