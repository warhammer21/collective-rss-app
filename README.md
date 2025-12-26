# Provenance

A common architecture used for data collection.

Provenance collects and stores articles from [infoq.com](https://www.infoq.com/) and follows a
Netflix [[Conductor-esque](https://netflix.github.io/conductor/)](https://docs.conductor-oss.org/devguide/architecture/index.html) architecture.

### Quick start

Download the codebase.

Create a jar file without running tests.

```bash
./gradlew assemble
```

### Articles

Run the articles component tests to see what's failing.

```bash
./gradlew :components:articles:test
```

Review the *todo* comments in the `ArticlesController` class and get the tests to pass. Along the way it will be helpful
to use the `writeJsonBody` method to convert articles to json.

```java
writeJsonBody(servletResponse, articles);
```

### Endpoints

Run the endpoints component tests to see what's failing.

```bash
./gradlew :components:endpoints:test  
```

Review the *todo* comments in the EndpointWorker class and get the tests to pass. Along the way it will be helpful to
use `XmlMapper` to convert RSS feeds to Java objects.

```java
RSS rss = new XmlMapper().readValue(response, RSS.class);
```

### Test suite

Ensure all the tests pass.

```bash
./gradlew build
```

### Schedule work

Review *todo* comments in the `App` class within the provenance-server component. Create and start a `WorkScheduler`.

```java
WorkScheduler<EndpointTask> scheduler = new WorkScheduler<>(finder, workers, 300);
``` 

_Pro tip:_ review the `testScheduler` test in the `WorkSchedulerTest` class.

### Run locally

Build the application again then run it locally to ensure that the endpoint worker is collecting articles.

```bash
./gradlew build
java -jar applications/provenance-server/build/libs/provenance-server-1.0-SNAPSHOT.jar 
```

Make a request for all articles in another terminal window.

```bash
curl -H "Accept: application/json" http://localhost:8881/articles
```

## Run with Docker

1. Build with Docker.
   ```bash
    docker build -t provenance-server . --platform linux/amd64
    ```

1. Run with Docker.
   ```bash
   docker run -p 8881:8881 provenance-server
   ```
Orchestration vs. Choreography: Explored the trade-offs of centralized control (Mediator) versus distributed events (Broker), focusing on State Management and Idempotency.
