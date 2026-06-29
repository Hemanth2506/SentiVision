import os
import sys
import io
import csv
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.prediction import Prediction, PredictionResponse, PredictionCreate
from middleware.auth import get_current_user

logger = logging.getLogger("sentivision.analyze")

# Add project root to sys.path to allow imports from ml/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ml.predict import predict_sentiment

router = APIRouter(tags=["analysis"])

@router.post("/analyze", response_model=PredictionResponse)
def analyze_text(
    payload: PredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze the sentiment of a single block of text and save to the history.
    """
    if not payload.input_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text content cannot be empty."
        )
    
    try:
        # Run ML prediction
        prediction_result = predict_sentiment(payload.input_text)
        
        # Save to database
        db_prediction = Prediction(
            user_id=current_user.id,
            input_text=payload.input_text,
            sentiment=prediction_result['sentiment'],
            confidence=prediction_result['confidence'],
            pos_prob=prediction_result['probabilities']['positive'],
            neg_prob=prediction_result['probabilities']['negative'],
            neu_prob=prediction_result['probabilities']['neutral']
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        logger.info(f"User {current_user.email} analyzed text. Sentiment: {db_prediction.sentiment}")
        return db_prediction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during sentiment prediction for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during sentiment analysis."
        )


@router.post("/analyze/batch", response_model=List[PredictionResponse])
def analyze_batch(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform bulk prediction by uploading a CSV or TXT file.
    Saves all valid predictions to the database.
    """
    filename = file.filename.lower()
    if not (filename.endswith('.csv') or filename.endswith('.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV and TXT files are supported."
        )
    
    try:
        contents = file.file.read()
        # Decode as utf-8 (ignoring errors)
        text_content = contents.decode("utf-8", errors="ignore")
        
        texts_to_analyze = []
        
        if filename.endswith('.csv'):
            # Parse CSV
            reader = csv.reader(io.StringIO(text_content))
            rows = list(reader)
            if not rows:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uploaded CSV file is empty."
                )
            
            # Check for header
            header_indices = ["text", "review", "content", "tweet", "message", "body"]
            header = [h.strip().lower() for h in rows[0]]
            text_col_idx = 0
            
            # Find the best column index for text content
            col_found = False
            for idx, col_name in enumerate(header):
                if any(h in col_name for h in header_indices):
                    text_col_idx = idx
                    col_found = True
                    break
            
            start_row = 1 if col_found else 0
            
            for row in rows[start_row:]:
                if not row or text_col_idx >= len(row):
                    continue
                val = row[text_col_idx].strip()
                if val:
                    texts_to_analyze.append(val)
        else:
            # Parse TXT (each line is a text record)
            lines = text_content.splitlines()
            for line in lines:
                val = line.strip()
                if val:
                    texts_to_analyze.append(val)
        
        if not texts_to_analyze:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No readable text records found in the uploaded file."
            )
        
        # Limit batch size to prevent server overload
        MAX_BATCH_SIZE = 500
        if len(texts_to_analyze) > MAX_BATCH_SIZE:
            texts_to_analyze = texts_to_analyze[:MAX_BATCH_SIZE]
            logger.warning(f"Batch truncated to {MAX_BATCH_SIZE} items for user {current_user.email}")
            
        results = []
        for text in texts_to_analyze:
            pred = predict_sentiment(text)
            db_prediction = Prediction(
                user_id=current_user.id,
                input_text=text,
                sentiment=pred['sentiment'],
                confidence=pred['confidence'],
                pos_prob=pred['probabilities']['positive'],
                neg_prob=pred['probabilities']['negative'],
                neu_prob=pred['probabilities']['neutral']
            )
            db.add(db_prediction)
            results.append(db_prediction)
            
        db.commit()
        for res in results:
            db.refresh(res)
            
        logger.info(f"User {current_user.email} successfully analyzed batch of {len(results)} items.")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing batch for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process the uploaded file."
        )
