import java.util.*;
import java.util.concurrent.*;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;


public class RequestMaker {
    private BotJava bot;
    public RequestMaker(BotJava bot)
    {
        this.bot = bot;
    }
    static int numThreads = 20;

    private String makeFutureTask (String xml){
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.add("X-EBAY-SOA-SERVICE-NAME", "FindingService");
        headers.add("X-EBAY-SOA-OPERATION-NAME", "findItemsByKeywords");
        headers.add("X-EBAY-SOA-SECURITY-APPNAME","Anastasi-EbayBot-PRD-2246ab0a7-f15336fc");
        headers.add("Content-Type", "text/xml");
        HttpEntity<String> request = new HttpEntity<String>(xml, headers);
        ResponseEntity<String> response = restTemplate.postForEntity
                ("http://svcs.ebay.com/services/search/FindingService/v1",
                        request, String.class);
        return response.toString();
    }

    public String request(String xmls) throws Exception {
        List<Future<String>> results = new LinkedList<>();
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        System.out.println("start_request");
        for (String i: xmls.split(";")) {
            Callable<String> task = () -> {
                String res = makeFutureTask(i);
                return res;
            };
            results.add(executor.submit(task));
        }
        String res = "";
        for (Future<String> result : results)
            res += result.get();
        bot.sendMessage("DONE");
        return res;
    }
}