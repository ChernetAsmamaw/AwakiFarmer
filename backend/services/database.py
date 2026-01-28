"""
Database Service - Data Persistence
Stores farmer profiles and conversation history
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

Base = declarative_base()


class Farmer(Base):
    """Farmer profile model"""
    __tablename__ = "farmers"
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    crops = Column(JSON, default=list)  # ["maize", "coffee"]
    language = Column(String(10), default="en")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    """Conversation history model"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    farmer_phone = Column(String(20), index=True, nullable=False)
    message_type = Column(String(20))  # "text", "image", "voice"
    user_message = Column(Text)
    ai_response = Column(Text)
    metadata = Column(JSON, nullable=True)  # disease predictions, weather data, etc.
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class DatabaseService:
    """Database service for managing farmer data"""
    
    def __init__(self):
        # Get database URL from environment or use SQLite for local dev
        database_url = os.getenv("DATABASE_URL", "sqlite:///./awakifarmer.db")
        
        # Handle SQLite special case
        if database_url.startswith("sqlite"):
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            self.engine = create_engine(database_url)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database initialized: {database_url}")
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def get_or_create_farmer(self, phone_number: str) -> Dict:
        """
        Get existing farmer or create new one
        
        Args:
            phone_number: Farmer's phone number
            
        Returns:
            Farmer data as dictionary
        """
        session = self.get_session()
        try:
            farmer = session.query(Farmer).filter(
                Farmer.phone_number == phone_number
            ).first()
            
            if not farmer:
                # Create new farmer
                farmer = Farmer(phone_number=phone_number)
                session.add(farmer)
                session.commit()
                session.refresh(farmer)
                logger.info(f"New farmer created: {phone_number}")
            else:
                # Update last active
                farmer.last_active = datetime.utcnow()
                session.commit()
            
            return {
                "id": farmer.id,
                "phone_number": farmer.phone_number,
                "name": farmer.name,
                "location": farmer.location,
                "crops": farmer.crops or [],
                "language": farmer.language,
                "created_at": farmer.created_at
            }
        
        finally:
            session.close()
    
    def update_farmer(
        self,
        phone_number: str,
        name: str = None,
        location: str = None,
        crops: List[str] = None,
        language: str = None
    ) -> bool:
        """
        Update farmer information
        
        Args:
            phone_number: Farmer's phone number
            name: Farmer's name (optional)
            location: Farmer's location (optional)
            crops: List of crops (optional)
            language: Preferred language (optional)
            
        Returns:
            True if successful
        """
        session = self.get_session()
        try:
            farmer = session.query(Farmer).filter(
                Farmer.phone_number == phone_number
            ).first()
            
            if not farmer:
                return False
            
            if name is not None:
                farmer.name = name
            if location is not None:
                farmer.location = location
            if crops is not None:
                farmer.crops = crops
            if language is not None:
                farmer.language = language
            
            session.commit()
            logger.info(f"Farmer updated: {phone_number}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating farmer: {str(e)}")
            session.rollback()
            return False
        
        finally:
            session.close()
    
    def save_conversation(
        self,
        farmer_phone: str,
        message_type: str,
        user_message: str,
        ai_response: str,
        metadata: Dict = None
    ) -> bool:
        """
        Save a conversation exchange
        
        Args:
            farmer_phone: Farmer's phone number
            message_type: Type of message (text/image/voice)
            user_message: What the farmer sent
            ai_response: What the AI responded
            metadata: Additional data (predictions, etc.)
            
        Returns:
            True if successful
        """
        session = self.get_session()
        try:
            conversation = Conversation(
                farmer_phone=farmer_phone,
                message_type=message_type,
                user_message=user_message,
                ai_response=ai_response,
                metadata=metadata
            )
            
            session.add(conversation)
            session.commit()
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            session.rollback()
            return False
        
        finally:
            session.close()
    
    def get_conversation_history(
        self,
        farmer_phone: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent conversation history
        
        Args:
            farmer_phone: Farmer's phone number
            limit: Number of conversations to retrieve
            
        Returns:
            List of conversation dictionaries
        """
        session = self.get_session()
        try:
            conversations = session.query(Conversation).filter(
                Conversation.farmer_phone == farmer_phone
            ).order_by(
                Conversation.created_at.desc()
            ).limit(limit).all()
            
            # Reverse to get chronological order
            conversations = list(reversed(conversations))
            
            return [
                {
                    "user_message": conv.user_message,
                    "ai_response": conv.ai_response,
                    "message_type": conv.message_type,
                    "metadata": conv.metadata,
                    "created_at": conv.created_at
                }
                for conv in conversations
            ]
        
        finally:
            session.close()
    
    def get_stats(self) -> Dict:
        """
        Get usage statistics
        
        Returns:
            Dictionary with stats
        """
        session = self.get_session()
        try:
            total_farmers = session.query(Farmer).count()
            active_farmers = session.query(Farmer).filter(
                Farmer.active == True
            ).count()
            total_conversations = session.query(Conversation).count()
            
            # Get recent activity (last 24 hours)
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            recent_messages = session.query(Conversation).filter(
                Conversation.created_at >= yesterday
            ).count()
            
            recent_farmers = session.query(Conversation).filter(
                Conversation.created_at >= yesterday
            ).distinct(Conversation.farmer_phone).count()
            
            return {
                "total_farmers": total_farmers,
                "active_farmers": active_farmers,
                "total_conversations": total_conversations,
                "messages_24h": recent_messages,
                "active_farmers_24h": recent_farmers
            }
        
        finally:
            session.close()
    
    def search_conversations(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search conversations by keyword
        
        Args:
            query: Search term
            limit: Max results
            
        Returns:
            List of matching conversations
        """
        session = self.get_session()
        try:
            conversations = session.query(Conversation).filter(
                Conversation.user_message.ilike(f"%{query}%")
            ).order_by(
                Conversation.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "farmer_phone": conv.farmer_phone,
                    "user_message": conv.user_message,
                    "ai_response": conv.ai_response,
                    "created_at": conv.created_at
                }
                for conv in conversations
            ]
        
        finally:
            session.close()
