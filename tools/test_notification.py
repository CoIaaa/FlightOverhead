<<<<<<< HEAD
#!/usr/bin/env python3
"""
Test script to verify desktop notifications work
"""

from plyer import notification
from datetime import datetime
import os

def test_notification():
    """Test the notification system with a sample flight"""
    
    title = "✈️ Flight Overhead: BA123"
    line2 = "British Airways | B77W - Boeing 777-300ER"
    route = "LHR → JFK"
    details = "35,000 ft | 450 kt"
    line3 = f"{route} | {details}"
    line4 = f"{datetime.now().strftime('%H:%M:%S')}"
    message = f"{line2}\n{line3}\n{line4}"
    
    print("Testing desktop notification...")
    print(f"Title: {title}")
    print(f"Message: {message}")
    
    # Robust icon selection
    icon_path = 'flight_icon.ico' if os.path.exists('flight_icon.ico') else None
    try:
        notification.notify(
            title=title,
            message=message,
            app_icon=icon_path,
            timeout=10,
        )
        print("✅ Notification sent successfully!")
        print("You should see a desktop notification appear.")
    except Exception as e:
        print(f"❌ Error showing notification: {e}")
        print("This might be due to Windows notification settings or permissions.")

if __name__ == "__main__":
=======
#!/usr/bin/env python3
"""
Test script to verify desktop notifications work
"""

from plyer import notification
from datetime import datetime
import os

def test_notification():
    """Test the notification system with a sample flight"""
    
    title = "✈️ Flight Overhead: BA123"
    line2 = "British Airways | B77W - Boeing 777-300ER"
    route = "LHR → JFK"
    details = "35,000 ft | 450 kt"
    line3 = f"{route} | {details}"
    line4 = f"{datetime.now().strftime('%H:%M:%S')}"
    message = f"{line2}\n{line3}\n{line4}"
    
    print("Testing desktop notification...")
    print(f"Title: {title}")
    print(f"Message: {message}")
    
    # Robust icon selection
    icon_path = 'flight_icon.ico' if os.path.exists('flight_icon.ico') else None
    try:
        notification.notify(
            title=title,
            message=message,
            app_icon=icon_path,
            timeout=10,
        )
        print("✅ Notification sent successfully!")
        print("You should see a desktop notification appear.")
    except Exception as e:
        print(f"❌ Error showing notification: {e}")
        print("This might be due to Windows notification settings or permissions.")

if __name__ == "__main__":
>>>>>>> eb3ab8304665a2eaf899ac0988e15ce17239d09e
    test_notification() 