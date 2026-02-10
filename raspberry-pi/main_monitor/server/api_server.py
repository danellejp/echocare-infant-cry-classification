"""
EchoCare - FastAPI Backend Server
Provides REST endpoints for the Android mobile app
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from contextlib import asynccontextmanager
import uvicorn
import os
import subprocess

# Import database module
from database import CryDatabase
from config import database_path

print("EchoCare FastAPI Server")
print(f"Database: {database_path}")

# ============================================================================
# Database Dependency (Creates connection per request)
# ============================================================================

def get_db():
    """
    Dependency that provides a database connection for each request
    Automatically closes connection when request is complete
    """
    db = CryDatabase(database_path)
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# Lifespan Context Manager (Replaces deprecated on_event)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages startup and shutdown events
    """
    # Startup
    print("\nFastAPI server started successfully")
    print(f"Access API at: http://localhost:8000")
    print(f"API docs at: http://localhost:8000/docs")
    print()
    
    yield  # Server runs during this yield
    
    # Shutdown
    print("\nShutting down FastAPI server...")
    print("Database connection closed")


# ============================================================================
# Initialize FastAPI App
# ============================================================================

app = FastAPI(
    title="EchoCare API",
    description="Backend API for EchoCare infant cry monitoring system",
    version="1.0.0",
    lifespan=lifespan  # Modern approach
)


# ============================================================================
# ENDPOINT 1: Health Check / Status
# ============================================================================

@app.get("/")
def root():
    """Root endpoint - API information"""
    return {
        "service": "EchoCare API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
def get_status(db: CryDatabase = Depends(get_db)):
    """
    Get Raspberry Pi connection status and system information
    
    Returns:
        - status: "online" or "offline"
        - timestamp: Current server time
        - database_connected: Boolean
        - total_events: Total cry events in database
    """
    try:
        # Check database connection
        total_events = db.get_total_events()
        
        return {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "database_connected": True,
            "total_events": total_events,
            "pi_info": {
                "hostname": os.uname().nodename,
                "system": os.uname().sysname
            }
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "database_connected": False
            }
        )


# ============================================================================
# ENDPOINT 2: Recent Events
# ============================================================================

@app.get("/recent-events")
def get_recent_events(limit: int = 10, db: CryDatabase = Depends(get_db)):
    """
    Get recent cry events
    
    Parameters:
        - limit: Number of recent events to return (default: 10, max: 50)
    
    Returns:
        - events: List of recent cry events
        - count: Number of events returned
    """
    try:
        # Validate limit
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 50"
            )
        
        # Get events from database
        events = db.get_recent_events(limit=limit)
        
        # Format events for JSON response
        formatted_events = []
        for event in events:
            event_id, timestamp, cry_type, detection_conf, class_conf, temp, humidity = event
            
            formatted_events.append({
                "id": event_id,
                "timestamp": timestamp,
                "cry_type": cry_type,
                "detection_confidence": round(detection_conf, 4),
                "classification_confidence": round(class_conf, 4),
                "temperature": round(temp, 1) if temp >= 0 else None,
                "humidity": round(humidity, 1) if humidity >= 0 else None
            })
        
        return {
            "events": formatted_events,
            "count": len(formatted_events),
            "limit": limit
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINT 3: Statistics (For Dashboard)
# ============================================================================

@app.get("/statistics")
def get_statistics(hours: int = 24, db: CryDatabase = Depends(get_db)):
    """
    Get cry statistics for dashboard
    
    Parameters:
        - hours: Time window in hours (default: 24)
    
    Returns:
        - total_cries: Total number of cry events
        - by_type: Breakdown by cry type (Hungry, Pain, Normal)
        - average_confidence: Average classification confidence
        - temperature_stats: Temperature data (if available)
        - humidity_stats: Humidity data (if available)
    """
    try:
        # Validate hours parameter
        if hours < 1 or hours > 168:  # Max 1 week
            raise HTTPException(
                status_code=400,
                detail="Hours must be between 1 and 168 (1 week)"
            )
        
        # Get statistics from database
        stats = db.get_statistics(hours=hours)
        
        return {
            "time_window_hours": hours,
            "statistics": stats,
            "generated_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ============================================================================
# Endpoint to get Android phone's time to send to Pi
# ============================================================================

@app.post("/set-time")
def set_time(data: dict):
    """
    Accept time from the Android app to sync Pi's clock.
    The Pi has no internet, so it relies on the phone's time.
    """
    try:
        time_string = data.get("datetime")
        if not time_string:
            return JSONResponse(status_code=400, content={"error": "datetime field required"})
        
        subprocess.run(['sudo', 'date', '-s', time_string], check=True)
        
        return {
            "status": "success",
            "pi_time": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============================================================================
# Run Server (for testing)
# ============================================================================

if __name__ == "__main__":
    
    print("\nStarting EchoCare API Server...")
    print("Press Ctrl+C to stop\n")
    
    # Run the server
    uvicorn.run(
        app,
        host="192.168.4.1",
        port=8000,
        log_level="info"
    )