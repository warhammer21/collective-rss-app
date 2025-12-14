┌─────────────────────────────────────────────────────────────┐
│                        App.java                              │
│  (Main application - starts everything)                      │
└─────────────────────────────────────────────────────────────┘
         │
         ├──→ REST API (already working)
         │    └── ArticlesController → ArticleDataGateway
         │
         └──→ Background Worker (TODO - you need to start this!)
              └── WorkScheduler


┌─────────────────────────────────────────────────────────────┐
│                   Background Worker Flow                     │
└─────────────────────────────────────────────────────────────┘

WorkScheduler (timer - runs every 10 seconds)
    ↓
Asks: EndpointWorkFinder.findRequested("ready")
    ↓
EndpointWorkFinder → EndpointDataGateway.findReady("ready")
    ↓
Returns: [EndpointTask("https://feed.infoq.com/")]
    ↓
WorkScheduler gives task to: EndpointWorker
    ↓
EndpointWorker.execute(task):
    1. Fetch XML from URL using RestTemplate
    2. Parse XML → RSS → Channel → Items
    3. Convert Items to ArticleInfo objects
    4. Save to ArticleDataGateway
    ↓
WorkScheduler marks task complete

visual 
┌─────────────────────────────────────┐
│         App.java Process            │
│  (Single JVM, Port 8881)            │
│                                     │
│  Thread 1: Jetty (REST API)         │
│  Thread 2: WorkScheduler            │
│  Thread 3: EndpointWorker           │
│  Thread 4: EndpointWorker           │
│  ...                                │
└─────────────────────────────────────┘

app.start()
    ↓
├─→ super.start() → Starts Jetty (REST API) on port 8881
│                   Thread 1, 2, 3... handling HTTP requests
│
└─→ WorkScheduler.start() → Starts background worker
                            Thread 4, 5... running workers every 10 seconds

## How It All Works Together
```
App.start()
    ↓
├─→ super.start() → Jetty starts
│                   API listening on http://localhost:8881
│                   GET /articles → ArticlesController → articleDataGateway
│
└─→ WorkScheduler.start() → Background worker starts
                            Every 10 seconds:
                              - Fetch from InfoQ
                              - Save to articleDataGateway
                              
Both running simultaneously!
API serves whatever is in articleDataGateway
Worker keeps updating articleDataGateway