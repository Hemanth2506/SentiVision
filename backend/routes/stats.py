from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func, desc, case
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.prediction import Prediction, PredictionResponse, HistoryResponse, StatsResponse
from middleware.auth import get_current_user
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("sentivision.stats")

router = APIRouter(tags=["stats"])

@router.get("/history", response_model=HistoryResponse)
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    sentiment: str = Query(None)
):
    """
    Fetch user's prediction history with support for pagination, search, and sentiment filter.
    """
    try:
        query = db.query(Prediction).filter(Prediction.user_id == current_user.id)
        
        # Apply search filter (case-insensitive search in input_text)
        if search:
            query = query.filter(Prediction.input_text.ilike(f"%{search}%"))
            
        # Apply sentiment filter
        if sentiment:
            query = query.filter(Prediction.sentiment == sentiment)
            
        # Get total count before pagination
        total_count = query.count()
        
        # Apply ordering (newest first) and pagination
        predictions = query.order_by(desc(Prediction.created_at))\
                           .offset((page - 1) * limit)\
                           .limit(limit)\
                           .all()
                           
        return {
            "total": total_count,
            "page": page,
            "limit": limit,
            "results": predictions
        }
    except Exception as e:
        logger.error(f"Error fetching history for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction history."
        )


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's dashboard statistics, charts data, and recent activity feed.
    """
    try:
        # 1. Total Predictions
        total = db.query(Prediction).filter(Prediction.user_id == current_user.id).count()
        
        if total == 0:
            # Return default empty states
            return {
                "kpis": {
                    "total": 0,
                    "positive_count": 0,
                    "positive_pct": 0.0,
                    "negative_count": 0,
                    "negative_pct": 0.0,
                    "neutral_count": 0,
                    "neutral_pct": 0.0
                },
                "pie_chart": {"positive": 0, "negative": 0, "neutral": 0},
                "bar_chart": [],
                "trend_chart": [],
                "recent_activity": []
            }
            
        # 2. Get counts per sentiment
        sentiment_counts = db.query(
            Prediction.sentiment, func.count(Prediction.id)
        ).filter(
            Prediction.user_id == current_user.id
        ).group_by(
            Prediction.sentiment
        ).all()
        
        counts_dict = {"Positive": 0, "Negative": 0, "Neutral": 0, "Neutral/Uncertain": 0}
        for sent, count in sentiment_counts:
            if sent in counts_dict:
                counts_dict[sent] = count
                
        pos_count = counts_dict["Positive"]
        neg_count = counts_dict["Negative"]
        # Neutral includes both "Neutral" and "Neutral/Uncertain"
        neu_count = counts_dict["Neutral"] + counts_dict["Neutral/Uncertain"]
        
        kpis = {
            "total": total,
            "positive_count": pos_count,
            "positive_pct": round((pos_count / total) * 100, 2),
            "negative_count": neg_count,
            "negative_pct": round((neg_count / total) * 100, 2),
            "neutral_count": neu_count,
            "neutral_pct": round((neu_count / total) * 100, 2),
        }
        
        # 3. Pie Chart (raw counts or pct)
        pie_chart = {
            "positive": pos_count,
            "negative": neg_count,
            "neutral": neu_count
        }
        
        # 4. Bar Chart & Trend line graph (Last 7 days data)
        # We group predictions by date
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=6) # 7 days including today
        
        # Fetch daily counts grouped by date
        # Format SQLite date extraction: strftime('%Y-%m-%d', created_at)
        date_group_func = func.strftime('%Y-%m-%d', Prediction.created_at)
        
        daily_stats = db.query(
            date_group_func.label('date'),
            func.count(Prediction.id).label('count'),
            func.avg(
                case(
                    (Prediction.sentiment == 'Positive', 1.0),
                    else_=0.0
                )
            ).label('pos_ratio')
        ).filter(
            Prediction.user_id == current_user.id,
            Prediction.created_at >= datetime.combine(start_date, datetime.min.time())
        ).group_by(
            'date'
        ).all()
        
        # Fill in missing dates for the last 7 days to ensure a clean chart
        daily_stats_map = {row.date: {"count": row.count, "pos_ratio": row.pos_ratio} for row in daily_stats}
        
        bar_chart = []
        trend_chart = []
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            if date_str in daily_stats_map:
                count = daily_stats_map[date_str]["count"]
                # Convert ratio to percentage
                pos_pct = round(daily_stats_map[date_str]["pos_ratio"] * 100, 2)
            else:
                count = 0
                pos_pct = 0.0
                
            bar_chart.append({"date": date_str, "count": count})
            # Trend shows sentiment score/positive % over time
            trend_chart.append({"date": date_str, "sentiment_score": pos_pct})
            
        # 5. Recent Activity Feed (Last 10 analyses)
        recent = db.query(Prediction).filter(
            Prediction.user_id == current_user.id
        ).order_by(
            desc(Prediction.created_at)
        ).limit(10).all()
        
        return {
            "kpis": kpis,
            "pie_chart": pie_chart,
            "bar_chart": bar_chart,
            "trend_chart": trend_chart,
            "recent_activity": recent
        }
    except Exception as e:
        logger.error(f"Error fetching stats for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics dashboard statistics."
        )


@router.delete("/stats/reset")
def reset_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete all prediction records for the current user.
    """
    try:
        db.query(Prediction).filter(Prediction.user_id == current_user.id).delete()
        db.commit()
        return {"message": "Data reset successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting predictions for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset prediction data."
        )

