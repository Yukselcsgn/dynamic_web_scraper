"""
Flask web dashboard for the Dynamic Web Scraper.
"""

import datetime
import json
import os
import queue

# Import scraper components
import sys
import threading

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.config import load_config
from scraper.core.scraper import Scraper
from scraper.css_selectors.dynamic_selector import DynamicSelector
from scraper.site_detection.html_analyzer import analyze_html, detect_ecommerce_patterns

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///scraper_dashboard.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Global variables for job management
active_jobs = {}
job_queue = queue.Queue()
job_results = {}


class ScrapingJob(db.Model):
    """Database model for scraping jobs."""

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    status = db.Column(
        db.String(50), default="pending"
    )  # pending, running, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    results_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)
    output_file = db.Column(db.String(200), nullable=True)
    site_type = db.Column(db.String(100), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)


class ScrapingResult(db.Model):
    """Database model for scraping results."""

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("scraping_job.id"), nullable=False)
    product_title = db.Column(db.String(500), nullable=True)
    product_price = db.Column(db.String(100), nullable=True)
    product_image = db.Column(db.String(500), nullable=True)
    product_link = db.Column(db.String(500), nullable=True)
    scraped_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


@app.route("/")
def index():
    """Main dashboard page."""
    # Get recent jobs
    recent_jobs = (
        ScrapingJob.query.order_by(ScrapingJob.created_at.desc()).limit(10).all()
    )

    # Get statistics
    total_jobs = ScrapingJob.query.count()
    completed_jobs = ScrapingJob.query.filter_by(status="completed").count()
    failed_jobs = ScrapingJob.query.filter_by(status="failed").count()
    running_jobs = ScrapingJob.query.filter_by(status="running").count()

    # Get total results
    total_results = ScrapingResult.query.count()

    stats = {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "running_jobs": running_jobs,
        "total_results": total_results,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
    }

    return render_template(
        "index.html", recent_jobs=recent_jobs, stats=stats, active_jobs=active_jobs
    )


@app.route("/start_scraping", methods=["GET", "POST"])
def start_scraping():
    """Start a new scraping job."""
    if request.method == "POST":
        url = request.form.get("url")
        output_format = request.form.get("output_format", "csv")

        if not url:
            flash("URL is required!", "error")
            return redirect(url_for("index"))

        # Create new job
        job = ScrapingJob(url=url, status="pending")
        db.session.add(job)
        db.session.commit()

        # Add to queue
        job_queue.put({"job_id": job.id, "url": url, "output_format": output_format})

        flash(f"Scraping job started for {url}", "success")
        return redirect(url_for("job_status", job_id=job.id))

    return render_template("start_scraping.html")


@app.route("/job/<int:job_id>")
def job_status(job_id):
    """Show job status and results."""
    job = ScrapingJob.query.get_or_404(job_id)
    results = ScrapingResult.query.filter_by(job_id=job_id).all()

    return render_template("job_status.html", job=job, results=results)


@app.route("/api/job/<int:job_id>/status")
def api_job_status(job_id):
    """API endpoint for job status."""
    job = ScrapingJob.query.get_or_404(job_id)

    return jsonify(
        {
            "id": job.id,
            "url": job.url,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "results_count": job.results_count,
            "error_message": job.error_message,
            "site_type": job.site_type,
            "confidence_score": job.confidence_score,
        }
    )


@app.route("/jobs")
def jobs_list():
    """List all scraping jobs."""
    page = request.args.get("page", 1, type=int)
    jobs = ScrapingJob.query.order_by(ScrapingJob.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template("jobs_list.html", jobs=jobs)


@app.route("/results")
def results_list():
    """List all scraping results."""
    page = request.args.get("page", 1, type=int)
    results = ScrapingResult.query.order_by(ScrapingResult.scraped_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    return render_template("results_list.html", results=results)


@app.route("/settings")
def settings():
    """Settings page for scraper configuration."""
    config = load_config()

    if request.method == "POST":
        # Update configuration
        config["use_proxy"] = request.form.get("use_proxy") == "on"
        config["max_retries"] = int(request.form.get("max_retries", 3))
        config["retry_delay"] = int(request.form.get("retry_delay", 2))

        # Save configuration
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)

        flash("Settings updated successfully!", "success")
        return redirect(url_for("settings"))

    return render_template("settings.html", config=config)


@app.route("/site_analysis")
def site_analysis():
    """Site analysis page."""
    return render_template("site_analysis.html")


@app.route("/api/analyze_site", methods=["POST"])
def api_analyze_site():
    """API endpoint for site analysis."""
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Load configuration
        config = load_config()

        # Create scraper instance
        scraper = Scraper(url, config)

        # Fetch HTML content
        response = scraper.fetch_data()

        if not response:
            return jsonify({"error": "Failed to fetch data from URL"}), 400

        # Analyze HTML
        analysis = analyze_html(response, url)
        patterns = detect_ecommerce_patterns(response)

        # Use dynamic selector
        dynamic_selector = DynamicSelector()
        selector_result = dynamic_selector.adapt_to_site(url, response)

        return jsonify(
            {"analysis": analysis, "patterns": patterns, "selectors": selector_result}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def process_job_queue():
    """Background worker to process scraping jobs."""
    while True:
        try:
            job_data = job_queue.get(timeout=1)
            process_scraping_job(job_data)
            job_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error processing job: {e}")


def process_scraping_job(job_data):
    """Process a single scraping job."""
    with app.app_context():
        job_id = job_data["job_id"]
        url = job_data["url"]
        output_format = job_data["output_format"]

        # Update job status
        job = ScrapingJob.query.get(job_id)
        if not job:
            return

        job.status = "running"
        active_jobs[job_id] = job
        db.session.commit()

        try:
            # Load configuration
            config = load_config()

            # Create scraper instance
            scraper = Scraper(url, config)

            # Fetch data
            data = scraper.fetch_data()

            if data:
                # Save results to database
                for item in data:
                    result = ScrapingResult(
                        job_id=job_id,
                        product_title=item.get("title", ""),
                        product_price=item.get("price", ""),
                        product_image=item.get("image", ""),
                        product_link=item.get("link", ""),
                    )
                    db.session.add(result)

                # Save to file
                output_file = f"data/scraped_data_{job_id}.{output_format}"
                scraper.save_data(data, output_file, output_format)

                # Update job status
                job.status = "completed"
                job.completed_at = datetime.datetime.utcnow()
                job.results_count = len(data)
                job.output_file = output_file

                # Get site analysis
                try:
                    analyze_html(data, url)
                    patterns = detect_ecommerce_patterns(data)
                    job.site_type = patterns.get("site_type", "unknown")
                    job.confidence_score = patterns.get("confidence_score", 0)
                except:
                    pass

            else:
                job.status = "failed"
                job.error_message = "No data found"
                job.completed_at = datetime.datetime.utcnow()

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.datetime.utcnow()

        finally:
            if job_id in active_jobs:
                del active_jobs[job_id]
            db.session.commit()


@app.before_request
def create_tables():
    """Create database tables."""
    db.create_all()


@app.before_request
def start_background_worker():
    """Start background worker thread."""
    worker_thread = threading.Thread(target=process_job_queue, daemon=True)
    worker_thread.start()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
