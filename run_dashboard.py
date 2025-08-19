#!/usr/bin/env python3
"""
Launcher script for the Dynamic Web Scraper Dashboard.
"""
import os
import sys
import webbrowser
import threading
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Launch the web dashboard."""
    print("🚀 Starting Dynamic Web Scraper Dashboard...")
    print("=" * 50)

    try:
        # Import and run the Flask app
        from scraper.dashboard.app import app

        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Start the Flask app in a separate thread
        def run_app():
            app.run(debug=False, host="0.0.0.0", port=5000)

        app_thread = threading.Thread(target=run_app, daemon=True)
        app_thread.start()

        # Wait a moment for the server to start
        time.sleep(2)

        # Open the dashboard in the default browser
        print("🌐 Opening dashboard in your browser...")
        webbrowser.open("http://localhost:5000")

        print("✅ Dashboard is running!")
        print("📊 Access it at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)

        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down dashboard...")
            print("✅ Goodbye!")

    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return 1

    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
