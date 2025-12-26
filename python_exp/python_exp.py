"""
Complete Python implementation of the Netflix Conductor-style
worker-task queue architecture, matching the Kotlin version.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Optional
import requests


# ═══════════════════════════════════════════════════════════════
# 1. DATA MODELS (Like ArticleRecord, EndpointRecord)
# ═══════════════════════════════════════════════════════════════

class ArticleRecord:
    """Represents a single article (like Java's ArticleRecord)"""
    def __init__(self, id: int, title: str, available: bool):
        self.id = id
        self.title = title
        self.available = available
    
    def __repr__(self):
        return f"ArticleRecord(id={self.id}, title='{self.title}', available={self.available})"


class ArticleInfo:
    """Response format for API (like Java's ArticleInfo)"""
    def __init__(self, id: int, title: str, available: bool):
        self.id = id
        self.title = title
        self.available = available
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'available': self.available
        }


class EndpointRecord:
    """Represents an endpoint to poll"""
    def __init__(self, url: str, status: str = "ready"):
        self.url = url
        self.status = status
    
    def __repr__(self):
        return f"EndpointRecord(url='{self.url}', status='{self.status}')"


class EndpointTask:
    """Task to be executed by worker"""
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
    
    def get_endpoint(self):
        return self.endpoint
    
    def __repr__(self):
        return f"EndpointTask(endpoint='{self.endpoint}')"


# ═══════════════════════════════════════════════════════════════
# 2. GATEWAYS (Data Access Layer)
# ═══════════════════════════════════════════════════════════════

class ArticleDataGateway:
    """
    Manages article data (like Java's ArticleDataGateway)
    This is where articles are stored in memory
    """
    def __init__(self, initial_records: List[ArticleRecord] = None):
        self._articles = []
        self._lock = threading.Lock()  # Thread-safe
        
        if initial_records:
            self._articles.extend(initial_records)
        
        print(f"📦 ArticleDataGateway initialized with {len(self._articles)} articles")
    
    def find_all(self) -> List[ArticleRecord]:
        """Get all articles"""
        with self._lock:
            return list(self._articles)  # Return copy
    
    def find_available(self) -> List[ArticleRecord]:
        """Get only available articles"""
        with self._lock:
            return [a for a in self._articles if a.available]
    
    def save(self, title: str):
        """Add new article"""
        with self._lock:
            new_id = len(self._articles) + 1
            article = ArticleRecord(new_id, title, True)
            self._articles.append(article)
            print(f"💾 Saved article: {title}")
    
    def clear(self):
        """Remove all articles"""
        with self._lock:
            self._articles.clear()


class EndpointDataGateway:
    """
    Manages endpoint tasks (like Java's EndpointDataGateway)
    Stores which RSS feeds to poll
    """
    def __init__(self):
        self._endpoints = [
            EndpointRecord("https://feed.infoq.com/", "ready"),
            # Add more endpoints here if needed
        ]
        self._lock = threading.Lock()
        
        print(f"🌐 EndpointDataGateway initialized with {len(self._endpoints)} endpoints")
    
    def find_ready(self, worker_name: str) -> List[EndpointRecord]:
        """Find endpoints ready to be processed"""
        with self._lock:
            return [e for e in self._endpoints if e.status == "ready"]
    
    def mark_completed(self, endpoint: str):
        """Mark endpoint as completed (for this cycle)"""
        with self._lock:
            for e in self._endpoints:
                if e.url == endpoint:
                    e.status = "completed"
                    print(f"✅ Marked {endpoint} as completed")
    
    def reset_all_to_ready(self):
        """Reset all endpoints to ready (for next polling cycle)"""
        with self._lock:
            for e in self._endpoints:
                e.status = "ready"


# ═══════════════════════════════════════════════════════════════
# 3. WORK FINDER (Finds tasks to execute)
# ═══════════════════════════════════════════════════════════════

class EndpointWorkFinder:
    """
    Finds work to do (like Java's EndpointWorkFinder)
    Acts as the "task queue" interface
    """
    def __init__(self, endpoint_gateway: EndpointDataGateway):
        self.endpoint_gateway = endpoint_gateway
        print("🔍 EndpointWorkFinder initialized")
    
    def find_requested(self, worker_name: str) -> List[EndpointTask]:
        """
        Find tasks for this worker
        (Like Kotlin's finder.findRequested(worker.name))
        """
        print(f"🔎 Finding tasks for {worker_name}...")
        
        # Get ready endpoints from gateway
        ready_endpoints = self.endpoint_gateway.find_ready(worker_name)
        
        # Convert to tasks
        tasks = [EndpointTask(endpoint.url) for endpoint in ready_endpoints]
        
        if tasks:
            print(f"📋 Found {len(tasks)} task(s) for {worker_name}")
        else:
            print(f"📋 No tasks found for {worker_name}")
        
        return tasks
    
    def mark_completed(self, task: EndpointTask):
        """Mark task as completed"""
        self.endpoint_gateway.mark_completed(task.get_endpoint())


# ═══════════════════════════════════════════════════════════════
# 4. WORKER (Executes tasks)
# ═══════════════════════════════════════════════════════════════

class RestTemplate:
    """Simple HTTP client (like Java's RestTemplate)"""
    def get(self, url: str) -> str:
        """Fetch URL and return content"""
        print(f"🌐 Fetching {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text


class EndpointWorker:
    """
    Worker that fetches RSS feeds and saves articles
    (Like Java's EndpointWorker)
    """
    def __init__(self, rest_template: RestTemplate, article_gateway: ArticleDataGateway, name: str = "EndpointWorker"):
        self.rest_template = rest_template
        self.article_gateway = article_gateway
        self.name = name
        print(f"👷 {self.name} initialized")
    
    def execute(self, task: EndpointTask):
        """
        Execute the task: fetch RSS, parse, save articles
        (Like Kotlin's worker.execute(it))
        """
        start_time = time.time()
        thread_name = threading.current_thread().name
        
        print(f"🔧 [{thread_name}] {self.name} starting task: {task.get_endpoint()}")
        
        try:
            # Fetch RSS feed
            xml_content = self.rest_template.get(task.get_endpoint())
            
            # Parse RSS (simplified - in real version, parse XML properly)
            # For demo, just save a sample article
            article_title = f"Article from {task.get_endpoint()} at {datetime.now().strftime('%H:%M:%S')}"
            self.article_gateway.save(article_title)
            
            duration = time.time() - start_time
            print(f"✅ [{thread_name}] {self.name} completed task in {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ [{thread_name}] {self.name} failed after {duration:.2f}s: {e}")
            raise


# ═══════════════════════════════════════════════════════════════
# 5. WORK SCHEDULER (Orchestrates everything)
# ═══════════════════════════════════════════════════════════════

class WorkScheduler:
    """
    Schedules and executes work (EXACTLY like Kotlin's WorkScheduler)
    
    Two thread pools:
    - polling_pool: One thread per worker, checks for work every N seconds
    - execution_pool: Up to 10 threads that execute actual work
    """
    def __init__(self, finder, workers: List, delay_seconds: int = 10):
        self.finder = finder
        self.workers = workers
        self.delay_seconds = delay_seconds
        
        # TWO THREAD POOLS (like Kotlin's 'pool' and 'service')
        self.polling_pool = ThreadPoolExecutor(
            max_workers=len(workers),
            thread_name_prefix="polling"
        )
        self.execution_pool = ThreadPoolExecutor(
            max_workers=10,
            thread_name_prefix="execution"
        )
        
        self.running = False
        print(f"⚙️  WorkScheduler initialized with {len(workers)} workers, delay={delay_seconds}s")
    
    def start(self):
        """
        Start the scheduler (like Kotlin's start())
        Creates one polling thread per worker
        """
        if self.running:
            print("⚠️  Scheduler already running!")
            return
        
        self.running = True
        print(f"🚀 Starting WorkScheduler...")
        
        # Start one polling thread per worker
        for worker in self.workers:
            print(f"📅 Scheduling worker: {worker.name}")
            
            # Submit polling task to polling pool
            # (Like Kotlin's: pool.scheduleWithFixedDelay(checkForWork(worker), 0, delay, TimeUnit.SECONDS))
            self.polling_pool.submit(self._check_for_work_loop, worker)
        
        print(f"✅ WorkScheduler started with {len(self.workers)} polling threads")
    
    def shutdown(self):
        """Gracefully shutdown both pools"""
        print("🛑 Shutting down WorkScheduler...")
        self.running = False
        
        # Shutdown both pools
        self.execution_pool.shutdown(wait=True)
        self.polling_pool.shutdown(wait=True)
        
        print("✅ WorkScheduler shutdown complete")
    
    def _check_for_work_loop(self, worker):
        """
        Polling loop for one worker (runs in polling pool thread)
        (Like Kotlin's checkForWork() function)
        """
        thread_name = threading.current_thread().name
        print(f"🔄 [{thread_name}] Started polling loop for {worker.name}")
        
        while self.running:
            try:
                print(f"\n🔍 [{thread_name}] Checking for work for {worker.name}...")
                
                # Find tasks for this worker
                # (Like Kotlin's: finder.findRequested(worker.name))
                tasks = self.finder.find_requested(worker.name)
                
                # Execute each task in execution pool
                for task in tasks:
                    print(f"📤 [{thread_name}] Found work for {worker.name}, submitting to execution pool")
                    
                    # Submit to EXECUTION pool (different pool!)
                    # (Like Kotlin's: service.submit { worker.execute(it) })
                    self.execution_pool.submit(self._execute_task, worker, task)
                
                print(f"💤 [{thread_name}] Done checking for {worker.name}, sleeping {self.delay_seconds}s...")
                
            except Exception as e:
                print(f"❌ [{thread_name}] Error in polling loop: {e}")
            
            # Sleep until next check (but check if we should stop)
            for _ in range(self.delay_seconds):
                if not self.running:
                    break
                time.sleep(1)
        
        print(f"🔚 [{thread_name}] Polling loop for {worker.name} exited")
    
    def _execute_task(self, worker, task):
        """
        Execute a task (runs in execution pool thread)
        (Like the body of Kotlin's: service.submit { ... })
        """
        try:
            # Execute the task
            worker.execute(task)
            
            # Mark as completed
            # (Like Kotlin's: finder.markCompleted(it))
            self.finder.mark_completed(task)
            
            print(f"✅ Completed work for {worker.name}")
            
        except Exception as e:
            print(f"❌ Unable to complete work for {worker.name}: {e}")


# ═══════════════════════════════════════════════════════════════
# 6. REST API (Flask-like, simplified)
# ═══════════════════════════════════════════════════════════════

class ArticlesController:
    """
    REST API controller (like Java's ArticlesController)
    """
    def __init__(self, article_gateway: ArticleDataGateway):
        self.article_gateway = article_gateway
        print("🌐 ArticlesController initialized")
    
    def get_all_articles(self) -> List[dict]:
        """GET /articles - Return all articles"""
        print("📥 GET /articles")
        
        # Get all ArticleRecords
        all_articles = self.article_gateway.find_all()
        
        # Transform to ArticleInfo
        article_infos = []
        for record in all_articles:
            info = ArticleInfo(
                record.id,
                record.title,
                record.available
            )
            article_infos.append(info.to_dict())
        
        print(f"📤 Returning {len(article_infos)} articles")
        return article_infos
    
    def get_available_articles(self) -> List[dict]:
        """GET /available - Return only available articles"""
        print("📥 GET /available")
        
        # Get available ArticleRecords
        available_articles = self.article_gateway.find_available()
        
        # Transform to ArticleInfo
        article_infos = []
        for record in available_articles:
            info = ArticleInfo(
                record.id,
                record.title,
                record.available
            )
            article_infos.append(info.to_dict())
        
        print(f"📤 Returning {len(article_infos)} available articles")
        return article_infos


# ═══════════════════════════════════════════════════════════════
# 7. MAIN APPLICATION (Like App.java)
# ═══════════════════════════════════════════════════════════════

class App:
    """
    Main application (like Java's App class)
    Sets up and starts everything
    """
    def __init__(self, port: int = 8881):
        self.port = port
        
        # Create gateways with initial data
        self.article_gateway = ArticleDataGateway([
            ArticleRecord(10101, "Programming Languages InfoQ Trends Report - October 2019", True),
            ArticleRecord(10106, "Ryan Kitchens on Learning from Incidents at Netflix", True)
        ])
        
        self.endpoint_gateway = EndpointDataGateway()
        
        # Create controller (REST API)
        self.controller = ArticlesController(self.article_gateway)
        
        # Create background worker components
        self.rest_template = RestTemplate()
        self.worker1 = EndpointWorker(self.rest_template, self.article_gateway, "Worker-1")
        self.worker2 = EndpointWorker(self.rest_template, self.article_gateway, "Worker-2")
        self.worker3 = EndpointWorker(self.rest_template, self.article_gateway, "Worker-3")
        
        self.finder = EndpointWorkFinder(self.endpoint_gateway)
        
        self.scheduler = WorkScheduler(
            self.finder,
            [self.worker1, self.worker2, self.worker3],
            delay_seconds=10
        )
        
        print(f"🎉 App initialized on port {self.port}")
    
    def start(self):
        """
        Start the application (like Java's app.start())
        """
        print("\n" + "="*60)
        print("🚀 STARTING APPLICATION")
        print("="*60 + "\n")
        
        # Start REST API (would normally start Flask/FastAPI here)
        print("🌐 REST API would start on port", self.port)
        print("   GET /articles - available")
        print("   GET /available - available")
        
        # Start background worker
        self.scheduler.start()
        
        print("\n✅ Application started successfully!")
        print("="*60 + "\n")
    
    def stop(self):
        """Stop the application"""
        print("\n" + "="*60)
        print("🛑 STOPPING APPLICATION")
        print("="*60 + "\n")
        
        self.scheduler.shutdown()
        
        print("✅ Application stopped")
        print("="*60 + "\n")
    
    def simulate_api_calls(self):
        """Simulate REST API calls"""
        print("\n" + "="*60)
        print("🌐 SIMULATING REST API CALLS")
        print("="*60 + "\n")
        
        # GET /articles
        articles = self.controller.get_all_articles()
        print(f"\nGET /articles returned {len(articles)} articles:")
        for article in articles[:3]:  # Show first 3
            print(f"  - {article}")
        if len(articles) > 3:
            print(f"  ... and {len(articles) - 3} more")
        
        print()
        
        # GET /available
        available = self.controller.get_available_articles()
        print(f"\nGET /available returned {len(available)} available articles")
        
        print("\n" + "="*60 + "\n")


# ═══════════════════════════════════════════════════════════════
# 8. MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def main():
    """
    Main entry point (like Java's main() method)
    """
    print("\n" + "="*60)
    print("🎬 NETFLIX CONDUCTOR PATTERN - PYTHON IMPLEMENTATION")
    print("="*60 + "\n")
    
    # Create app
    app = App(port=8881)
    
    # Start app (REST API + Background Worker)
    app.start()
    
    try:
        # Let it run and demonstrate
        print("⏰ Letting scheduler run for 30 seconds...\n")
        
        # Check articles every 10 seconds
        for i in range(3):
            time.sleep(10)
            print(f"\n{'='*60}")
            print(f"⏰ {(i+1)*10} seconds elapsed - Checking article count...")
            print(f"{'='*60}\n")
            app.simulate_api_calls()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        # Shutdown gracefully
        app.stop()
        print("\n👋 Program finished!")


if __name__ == "__main__":
    main()