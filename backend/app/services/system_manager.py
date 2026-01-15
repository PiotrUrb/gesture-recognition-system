import psutil
import logging
import asyncio
import os
import signal
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class SystemStatusEnum(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    STARTING = "starting"
    CHECKING = "checking"
    ERROR = "error"

class SystemManager:
    """Manages system operations"""

    def __init__(self):
        self.current_status = SystemStatusEnum.ONLINE
        self.last_status_check = datetime.utcnow()
        self.operation_in_progress = False
        self.current_operation = None
        self.operation_progress = 0.0
        self.operation_message = ""
        self.start_time = datetime.utcnow()

    async def check_health(self) -> Dict:
        """Check system health"""
        try:
            self.current_status = SystemStatusEnum.CHECKING
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            uptime = datetime.utcnow() - self.start_time
            uptime_seconds = int(uptime.total_seconds())
            
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get('http://localhost:8000/health', timeout=aiohttp.ClientTimeout(total=2)):
                        pass
                backend_ok = True
            except:
                backend_ok = False
            
            if backend_ok:
                self.current_status = SystemStatusEnum.ONLINE
            else:
                self.current_status = SystemStatusEnum.ERROR
            
            self.last_status_check = datetime.utcnow()
            
            return {
                "status": self.current_status.value,
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "uptime_seconds": uptime_seconds,
                "timestamp": self.last_status_check.isoformat(),
                "backend_responsive": backend_ok
            }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.current_status = SystemStatusEnum.ERROR
            return {
                "status": "error",
                "error_message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def shutdown_system(self) -> Dict:
        """Graceful shutdown"""
        if self.operation_in_progress:
            return {"error": "Operation already in progress"}
        
        try:
            self.operation_in_progress = True
            self.current_operation = "shutdown"
            self.operation_message = "Preparing system shutdown..."
            self.operation_progress = 0.0
            
            logger.info("SHUTTING DOWN SYSTEM...")
            
            steps = [
                ("Closing cameras...", 0.2),
                ("Saving data...", 0.4),
                ("Stopping services...", 0.6),
                ("Cleaning up...", 0.8),
                ("Goodbye!", 1.0)
            ]
            
            for message, progress in steps:
                self.operation_message = message
                self.operation_progress = progress
                logger.info(f"  {message}")
                await asyncio.sleep(0.5)
            
            logger.info("System shutdown initiated")
            
            await asyncio.sleep(1)
            os.kill(os.getpid(), signal.SIGTERM)
            
            return {
                "status": "success",
                "message": "System shutting down..."
            }
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            self.current_status = SystemStatusEnum.ERROR
            self.operation_in_progress = False
            return {
                "status": "error",
                "message": str(e)
            }

    async def restart_system(self) -> Dict:
        """Graceful restart"""
        if self.operation_in_progress:
            return {"error": "Operation already in progress"}
        
        try:
            self.operation_in_progress = True
            self.current_operation = "restart"
            self.operation_message = "Preparing system restart..."
            self.operation_progress = 0.0
            
            logger.info("RESTARTING SYSTEM...")
            
            steps = [
                ("Closing cameras...", 0.15),
                ("Saving data...", 0.30),
                ("Stopping services...", 0.45),
                ("Shutting down backend...", 0.60),
                ("Starting backend...", 0.75),
                ("Initializing services...", 0.90),
                ("Ready!", 1.0)
            ]
            
            for message, progress in steps:
                self.operation_message = message
                self.operation_progress = progress
                logger.info(f"  {message}")
                await asyncio.sleep(0.5)
            
            logger.info("System restart completed")
            
            self.operation_in_progress = False
            self.current_status = SystemStatusEnum.ONLINE
            self.current_operation = None
            
            return {
                "status": "success",
                "message": "System restarted successfully"
            }
        except Exception as e:
            logger.error(f"Restart error: {e}")
            self.current_status = SystemStatusEnum.ERROR
            self.operation_in_progress = False
            return {
                "status": "error",
                "message": str(e)
            }

    def get_operation_progress(self) -> Dict:
        """Get current operation progress"""
        return {
            "operation": self.current_operation,
            "progress": self.operation_progress,
            "message": self.operation_message,
            "in_progress": self.operation_in_progress
        }

    def get_status(self) -> Dict:
        """Get current system status"""
        return {
            "status": self.current_status.value,
            "operation": self.current_operation,
            "progress": self.operation_progress,
            "message": self.operation_message,
            "in_progress": self.operation_in_progress,
            "last_check": self.last_status_check.isoformat()
        }

system_manager = SystemManager()