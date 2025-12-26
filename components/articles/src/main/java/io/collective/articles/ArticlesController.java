package io.collective.articles;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.collective.restsupport.BasicHandler;
import org.eclipse.jetty.server.Request;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.ArrayList;
import java.util.List;

public class ArticlesController extends BasicHandler {
    private final ArticleDataGateway gateway;

    public ArticlesController(ObjectMapper mapper, ArticleDataGateway gateway) {
        super(mapper);
        this.gateway = gateway;
    }

    @Override
    public void handle(String target, Request request, HttpServletRequest servletRequest, HttpServletResponse servletResponse) {

        // ═══════════════════════════════════════════
        // GET /articles - Return ALL articles
        // ═══════════════════════════════════════════
        System.out.println("=== DEBUG ===");
        System.out.println("Request URI: " + request.getRequestURI());
        System.out.println("Request Method: " + request.getMethod());
        System.out.println("Accept Header: " + request.getHeader("Accept"));
        System.out.println("=============");
        System.out.println("ArticlesController handling: " + request.getRequestURI());
    
            
        get("/articles", List.of("application/json", "text/html"), request, servletResponse, () -> {
            // 1. Get all ArticleRecords from gateway
            List<ArticleRecord> all_articles = this.gateway.findAll();

            // 2. Create empty list to hold ArticleInfo objects
            List<ArticleInfo> article_infos = new ArrayList<>();

            // 3. Loop through each ArticleRecord
            for (int i = 0; i < all_articles.size(); i++) {
                // 4. GET the ArticleRecord at index i
                ArticleRecord record = all_articles.get(i);
                
                // 5. CREATE a NEW ArticleInfo object from the record's data
                ArticleInfo info = new ArticleInfo(
                    record.getId(),
                    record.getTitle()
                );
                
                // 6. ADD the ArticleInfo object to the list
                article_infos.add(info);
            }

            // 7. Return the list of ArticleInfo objects
            writeJsonBody(servletResponse, article_infos);
        });

        // ═══════════════════════════════════════════
        // GET /available - Return ONLY available articles
        // ═══════════════════════════════════════════
        get("/available", List.of("application/json"), request, servletResponse, () -> {
            // TODO - YOUR CODE HERE!
            // // todo - query the articles gateway for *available* articles, map records to infos, and send back a collection of article infos
              // 1. Get all ArticleRecords from gateway
            List<ArticleRecord> all_articles = this.gateway.findAvailable();

            // 2. Create empty list to hold ArticleInfo objects
            List<ArticleInfo> article_infos = new ArrayList<>();

            // 3. Loop through each ArticleRecord
            for (int i = 0; i < all_articles.size(); i++) {
                // 4. GET the ArticleRecord at index i
                ArticleRecord record = all_articles.get(i);
                
                // 5. CREATE a NEW ArticleInfo object from the record's data
                ArticleInfo info = new ArticleInfo(
                    record.getId(),
                    record.getTitle()
                );
                
                // 6. ADD the ArticleInfo object to the list
                article_infos.add(info);
            }
            writeJsonBody(servletResponse, article_infos);
        });
    }
}