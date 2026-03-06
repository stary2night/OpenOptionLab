"""
Notification Service
处理用户通知的发送和管理
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.models.user import UserNotification, User


class NotificationService:
    """Notification service for managing user notifications"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> UserNotification:
        """
        Create a new notification for a user
        
        Args:
            user_id: Target user ID
            notification_type: Type of notification (price_alert, system, etc.)
            title: Notification title
            message: Notification message
            data: Optional additional data
            
        Returns:
            Created notification
        """
        notification = UserNotification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data or {},
            is_read=False
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[UserNotification]:
        """
        Get notifications for a user
        
        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of notifications
        """
        query = select(UserNotification).where(
            UserNotification.user_id == user_id
        )
        
        if unread_only:
            query = query.where(UserNotification.is_read == False)
        
        query = query.order_by(desc(UserNotification.created_at))
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_unread_count(self, user_id: int) -> int:
        """
        Get unread notification count for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of unread notifications
        """
        result = await self.db.execute(
            select(func.count(UserNotification.id)).where(
                and_(
                    UserNotification.user_id == user_id,
                    UserNotification.is_read == False
                )
            )
        )
        return result.scalar()
    
    async def mark_as_read(
        self,
        notification_id: int,
        user_id: int
    ) -> Optional[UserNotification]:
        """
        Mark a notification as read
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for verification)
            
        Returns:
            Updated notification or None
        """
        result = await self.db.execute(
            select(UserNotification).where(
                and_(
                    UserNotification.id == notification_id,
                    UserNotification.user_id == user_id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(notification)
        
        return notification
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """
        Mark all notifications as read for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of notifications marked as read
        """
        result = await self.db.execute(
            select(UserNotification).where(
                and_(
                    UserNotification.user_id == user_id,
                    UserNotification.is_read == False
                )
            )
        )
        notifications = result.scalars().all()
        
        now = datetime.now()
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now
        
        await self.db.commit()
        return len(notifications)
    
    async def delete_notification(
        self,
        notification_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a notification
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for verification)
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.db.execute(
            select(UserNotification).where(
                and_(
                    UserNotification.id == notification_id,
                    UserNotification.user_id == user_id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            await self.db.delete(notification)
            await self.db.commit()
            return True
        
        return False
    
    async def send_bulk_notification(
        self,
        user_ids: List[int],
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Send notification to multiple users
        
        Args:
            user_ids: List of target user IDs
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Optional additional data
            
        Returns:
            Number of notifications created
        """
        notifications = [
            UserNotification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                data=data or {},
                is_read=False
            )
            for user_id in user_ids
        ]
        
        self.db.add_all(notifications)
        await self.db.commit()
        
        return len(notifications)
    
    async def cleanup_old_notifications(self, days: int = 30) -> int:
        """
        Delete old read notifications
        
        Args:
            days: Delete notifications older than this many days
            
        Returns:
            Number of notifications deleted
        """
        cutoff_date = datetime.now() - __import__('datetime').timedelta(days=days)
        
        result = await self.db.execute(
            select(UserNotification).where(
                and_(
                    UserNotification.is_read == True,
                    UserNotification.read_at < cutoff_date
                )
            )
        )
        old_notifications = result.scalars().all()
        
        for notification in old_notifications:
            await self.db.delete(notification)
        
        await self.db.commit()
        return len(old_notifications)
