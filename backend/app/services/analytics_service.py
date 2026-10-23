"""Analytics service for dashboard metrics."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Chat, Message, Ticket, User, Feedback
from app.repositories.chat_repository import ChatRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository


class AnalyticsService:
    """Service for analytics and dashboard metrics."""

    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict:
        """Get dashboard metrics."""
        # Chat metrics
        total_chats = db.query(Chat).count()
        messages = db.query(Message).all()
        total_messages = len(messages)

        # Calculate average confidence score
        confidence_scores = [
            m.confidence_score for m in messages
            if m.confidence_score is not None
        ]
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores else 0.0
        )

        # Calculate average response time
        response_times = []
        messages_dict = {}
        for msg in messages:
            if msg.chat_id not in messages_dict:
                messages_dict[msg.chat_id] = []
            messages_dict[msg.chat_id].append(msg)

        for chat_messages in messages_dict.values():
            if len(chat_messages) >= 2:
                for i in range(1, len(chat_messages)):
                    if chat_messages[i].role == "assistant":
                        time_diff = (
                            chat_messages[i].created_at -
                            chat_messages[i-1].created_at
                        ).total_seconds()
                        if time_diff > 0:
                            response_times.append(time_diff)

        avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times else 0.0
        )

        # Ticket metrics
        ticket_stats = TicketRepository.get_ticket_statistics(db)

        # User metrics
        total_users = UserRepository.get_user_count(db)

        # Feedback metrics
        feedback = db.query(Feedback).all()
        user_satisfaction = (
            sum(f.rating for f in feedback) / len(feedback)
            if feedback else 0.0
        )

        return {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "total_tickets": ticket_stats["total"],
            "total_users": total_users,
            "avg_confidence_score": round(avg_confidence, 2),
            "avg_response_time": round(avg_response_time, 2),
            "user_satisfaction_score": round(user_satisfaction, 2),
            "ticket_resolution_rate": round(ticket_stats["resolution_rate"], 2),
            "open_tickets": ticket_stats["open"],
            "resolved_tickets": ticket_stats["resolved"],
            "closed_tickets": ticket_stats["closed"],
            "feedback_count": len(feedback)
        }

    @staticmethod
    def get_chat_analytics(db: Session, days: int = 7) -> dict:
        """Get chat analytics for last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_chats = db.query(Chat).filter(Chat.created_at >= cutoff_date).all()

        chats_by_date = {}
        for chat in recent_chats:
            date_key = chat.created_at.strftime("%Y-%m-%d")
            if date_key not in chats_by_date:
                chats_by_date[date_key] = 0
            chats_by_date[date_key] += 1

        return {
            "period_days": days,
            "total_chats": len(recent_chats),
            "chats_by_date": chats_by_date,
            "avg_chats_per_day": len(recent_chats) / days if days > 0 else 0
        }

    @staticmethod
    def get_ticket_analytics(db: Session, days: int = 7) -> dict:
        """Get ticket analytics for last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_tickets = db.query(Ticket).filter(Ticket.created_at >= cutoff_date).all()

        by_category = {}
        by_priority = {}
        by_status = {}

        for ticket in recent_tickets:
            # By category
            cat = ticket.category
            by_category[cat] = by_category.get(cat, 0) + 1

            # By priority
            pri = ticket.priority
            by_priority[pri] = by_priority.get(pri, 0) + 1

            # By status
            stat = ticket.status
            by_status[stat] = by_status.get(stat, 0) + 1

        return {
            "period_days": days,
            "total_tickets": len(recent_tickets),
            "by_category": by_category,
            "by_priority": by_priority,
            "by_status": by_status
        }

    @staticmethod
    def get_confidence_distribution(db: Session) -> dict:
        """Get confidence score distribution."""
        messages = db.query(Message).filter(Message.confidence_score.isnot(None)).all()

        ranges = {
            "0-20": 0,
            "20-40": 0,
            "40-60": 0,
            "60-80": 0,
            "80-100": 0
        }

        for msg in messages:
            score = msg.confidence_score * 100
            if score < 20:
                ranges["0-20"] += 1
            elif score < 40:
                ranges["20-40"] += 1
            elif score < 60:
                ranges["40-60"] += 1
            elif score < 80:
                ranges["60-80"] += 1
            else:
                ranges["80-100"] += 1

        return ranges

    @staticmethod
    def get_user_activity(db: Session, user_id: int) -> dict:
        """Get user activity metrics."""
        user_chats = ChatRepository.get_user_chats(db, user_id)
        user_tickets = TicketRepository.get_user_tickets(db, user_id)
        user_feedback = db.query(Feedback).filter(Feedback.user_id == user_id).all()

        # Calculate messages in user's chats
        user_messages = 0
        for chat in user_chats:
            user_messages += len(chat.messages) if hasattr(chat, 'messages') else 0

        return {
            "user_id": user_id,
            "total_chats": len(user_chats),
            "total_tickets": len(user_tickets),
            "total_messages": user_messages,
            "feedback_provided": len(user_feedback),
            "avg_feedback_rating": (
                sum(f.rating for f in user_feedback) / len(user_feedback)
                if user_feedback else 0.0
            )
        }
