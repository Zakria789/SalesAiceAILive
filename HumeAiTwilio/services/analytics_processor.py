"""
Auto-generate analytics when call completes
Process conversation logs and create analytics records
"""
import logging
from datetime import datetime
from django.db.models import Avg

from HumeAiTwilio.models import (
    TwilioCall, ConversationLog, ConversationAnalytics,
    CallObjection, CLARIFIESStep
)

logger = logging.getLogger(__name__)


class AnalyticsProcessor:
    """Process call data and generate analytics automatically"""
    
    @staticmethod
    def process_completed_call(call_sid):
        """
        Process a completed call and generate analytics
        Called from status callback when call ends
        """
        try:
            # Get the call
            call = TwilioCall.objects.get(call_sid=call_sid)
            
            # Skip if already analyzed
            if ConversationAnalytics.objects.filter(call=call).exists():
                logger.info(f"Call {call_sid} already analyzed, skipping")
                return
            
            # Get conversation logs
            logs = call.conversation_logs.all().order_by('timestamp')
            
            if logs.count() < 2:
                logger.warning(f"Call {call_sid} has insufficient conversation logs")
                return
            
            # Extract data from logs
            logs_list = list(logs)
            
            # 1. Calculate sentiment from HUME AI emotion scores
            sentiments = []
            emotions_list = []
            dominant_emotion = None
            
            for log in logs_list:
                # Extract Hume AI emotion scores
                if log.emotion_scores:
                    try:
                        import json
                        if isinstance(log.emotion_scores, str):
                            emotion_data = json.loads(log.emotion_scores)
                        else:
                            emotion_data = log.emotion_scores
                        
                        # Hume AI returns emotion scores like:
                        # {"Joy": 0.8, "Sadness": 0.1, "Anger": 0.05, ...}
                        if isinstance(emotion_data, dict):
                            # Calculate sentiment from emotion balance
                            positive_emotions = ['Joy', 'Contentment', 'Amusement', 'Love', 'Excitement', 'Satisfaction', 'Relief']
                            negative_emotions = ['Sadness', 'Anger', 'Fear', 'Disgust', 'Anxiety', 'Disappointment', 'Frustration']
                            
                            positive_score = sum([emotion_data.get(e, 0) for e in positive_emotions if e in emotion_data])
                            negative_score = sum([emotion_data.get(e, 0) for e in negative_emotions if e in emotion_data])
                            
                            # Net sentiment score (-1 to 1)
                            if positive_score + negative_score > 0:
                                sentiment_score = (positive_score - negative_score) / (positive_score + negative_score)
                                sentiments.append(sentiment_score)
                            
                            # Track emotions
                            emotions_list.extend(emotion_data.keys())
                            
                            # Get dominant emotion
                            if emotion_data:
                                top_emotion = max(emotion_data, key=emotion_data.get)
                                if not dominant_emotion or emotion_data[top_emotion] > 0.5:
                                    dominant_emotion = top_emotion
                    except Exception as e:
                        logger.warning(f"Error parsing emotion_scores for log: {e}")
                
                # Fallback to sentiment field if no emotion_scores
                if not sentiments and log.sentiment:
                    if log.sentiment.lower() == 'positive':
                        sentiments.append(0.7)
                    elif log.sentiment.lower() == 'negative':
                        sentiments.append(-0.7)
                    else:
                        sentiments.append(0.0)
            
            # Calculate average sentiment
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
            
            # Determine sentiment trend (matching model choices)
            if avg_sentiment > 0.2:
                sentiment_trend = 'improving'
            elif avg_sentiment < -0.2:
                sentiment_trend = 'declining'
            else:
                sentiment_trend = 'stable'
            
            # Get most common emotion
            if not dominant_emotion and emotions_list:
                from collections import Counter
                emotion_counts = Counter(emotions_list)
                dominant_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else None
            
            # 2. Detect outcome from last messages (matching model choices)
            last_messages = [log.message.lower() for log in logs_list[-3:] if log.message]
            outcome = 'follow_up'
            
            win_keywords = ['yes', 'interested', 'schedule', 'demo', 'sign up', 'agreement', 'deal', 'interested']
            loss_keywords = ['not interested', 'no thanks', 'not now', 'busy', 'call back later', 'not right now']
            
            last_text = ' '.join(last_messages)
            if any(word in last_text for word in win_keywords):
                outcome = 'won'
            elif any(word in last_text for word in loss_keywords):
                outcome = 'lost'
            
            # 3. Detect objections
            objection_keywords = {
                'price': ['expensive', 'cost', 'price', 'afford', 'budget'],
                'timing': ['busy', 'no time', 'later', 'schedule'],
                'need': ['not need', 'not interested', 'not right now'],
                'trust': ['not sure', 'doubt', 'guarantee', 'proven']
            }
            
            total_objections = 0
            objections_resolved = 0
            
            all_text = ' '.join([log.message.lower() for log in logs_list if log.message])
            
            # Track CLARIFIES steps used
            clarifies_steps = []
            
            # Detect and create objection records + CLARIFIES steps
            for obj_type, keywords in objection_keywords.items():
                if any(keyword in all_text for keyword in keywords):
                    total_objections += 1
                    objections_resolved += 1  # Assume resolved if call continued
                    
                    # Create CallObjection record
                    CallObjection.objects.create(
                        call=call,
                        objection_type=obj_type,
                        objection_text=f"Detected {obj_type} objection in conversation",
                        detected_at=datetime.now(),
                        clarifies_step='C',  # Concern identification
                        agent_response="Agent addressed the concern",
                        resolution_status='resolved',
                        confidence_score=0.7
                    )
                    
                    # Create CLARIFIESStep record
                    CLARIFIESStep.objects.create(
                        call=call,
                        step_type='C',
                        step_number=len(clarifies_steps) + 1,
                        effectiveness_score=0.7,
                        duration_seconds=30,
                        reasoning=f"Addressed {obj_type} objection",
                        timestamp=datetime.now()
                    )
                    clarifies_steps.append('C')
            
            # Add other CLARIFIES steps based on conversation flow
            if logs_count > 2:
                # Listen step (L) - always present if conversation happened
                CLARIFIESStep.objects.create(
                    call=call,
                    step_type='L',
                    step_number=1,
                    effectiveness_score=0.8,
                    duration_seconds=20,
                    reasoning="Active listening to customer",
                    timestamp=logs_list[0].timestamp if hasattr(logs_list[0], 'timestamp') else datetime.now()
                )
                if 'L' not in clarifies_steps:
                    clarifies_steps.insert(0, 'L')
            
            if outcome == 'won':
                # Seal step (S) - close the deal
                CLARIFIESStep.objects.create(
                    call=call,
                    step_type='S',
                    step_number=len(clarifies_steps) + 1,
                    effectiveness_score=0.9,
                    duration_seconds=45,
                    reasoning="Reached agreement with customer",
                    timestamp=datetime.now()
                )
                clarifies_steps.append('S')
            
            # 4. Create ConversationAnalytics record with Hume AI emotion data
            analytics = ConversationAnalytics.objects.create(
                call=call,
                total_objections=total_objections,
                objections_resolved=objections_resolved,
                objections_escalated=total_objections - objections_resolved,
                outcome=outcome,
                sentiment_trend=sentiment_trend,
                avg_sentiment=round(avg_sentiment, 3),  # -1 to 1 scale from Hume AI
                dominant_customer_emotion=dominant_emotion,  # Top emotion from Hume AI
                win_probability=0.7 if outcome == 'won' else (0.2 if outcome == 'lost' else 0.5),
                clarifies_steps_used=clarifies_steps,
                total_steps=len(clarifies_steps),
                analyzed_at=datetime.now()
            )
            
            logger.info(f"✅ Analytics created for call {call_sid}:")
            logger.info(f"   Outcome: {outcome}")
            logger.info(f"   Sentiment: {avg_sentiment:.2f} ({sentiment_trend})")
            logger.info(f"   Dominant Emotion: {dominant_emotion}")
            logger.info(f"   Objections: {total_objections} (Resolved: {objections_resolved})")
            
            return analytics
            
        except TwilioCall.DoesNotExist:
            logger.error(f"Call {call_sid} not found")
            return None
        except Exception as e:
            logger.error(f"Error processing call {call_sid}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_analytics_on_new_message(call_sid, message, role, emotion_scores=None):
        """
        Update analytics incrementally as new messages arrive
        Uses real-time Hume AI emotion scores
        Can be called from WebSocket message handler
        """
        try:
            import json
            call = TwilioCall.objects.get(call_sid=call_sid)
            
            # Get or create analytics
            analytics, created = ConversationAnalytics.objects.get_or_create(
                call=call,
                defaults={
                    'total_objections': 0,
                    'objections_resolved': 0,
                    'objections_escalated': 0,
                    'outcome': 'follow_up',
                    'sentiment_trend': 'stable',
                    'avg_sentiment': 0.0,
                    'win_probability': 0.5,
                    'analyzed_at': datetime.now()
                }
            )
            
            # Update sentiment running average from Hume AI emotion scores
            if emotion_scores:
                try:
                    if isinstance(emotion_scores, str):
                        emotion_data = json.loads(emotion_scores)
                    else:
                        emotion_data = emotion_scores
                    
                    # Calculate sentiment from Hume emotions
                    positive_emotions = ['Joy', 'Contentment', 'Amusement', 'Love', 'Excitement', 'Satisfaction', 'Relief']
                    negative_emotions = ['Sadness', 'Anger', 'Fear', 'Disgust', 'Anxiety', 'Disappointment', 'Frustration']
                    
                    positive_score = sum([emotion_data.get(e, 0) for e in positive_emotions if e in emotion_data])
                    negative_score = sum([emotion_data.get(e, 0) for e in negative_emotions if e in emotion_data])
                    
                    if positive_score + negative_score > 0:
                        sentiment_score = (positive_score - negative_score) / (positive_score + negative_score)
                        
                        # Update running average
                        logs_count = call.conversation_logs.count()
                        current_avg = analytics.avg_sentiment
                        new_avg = ((current_avg * logs_count) + sentiment_score) / (logs_count + 1)
                        
                        analytics.avg_sentiment = round(new_avg, 3)
                        
                        # Update sentiment trend (matching model choices)
                        if new_avg > 0.2:
                            analytics.sentiment_trend = 'improving'
                        elif new_avg < -0.2:
                            analytics.sentiment_trend = 'declining'
                        else:
                            analytics.sentiment_trend = 'stable'
                        
                        # Update dominant emotion
                        top_emotion = max(emotion_data, key=emotion_data.get)
                        if emotion_data[top_emotion] > 0.5:
                            analytics.dominant_customer_emotion = top_emotion
                        
                        analytics.save()
                        logger.info(f"📊 Real-time analytics updated: {call_sid} - Sentiment: {new_avg:.2f}")
                        
                except Exception as e:
                    logger.warning(f"Error parsing emotion scores: {e}")
            
        except Exception as e:
            logger.error(f"Error updating analytics for {call_sid}: {e}")
