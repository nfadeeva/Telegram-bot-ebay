import java.util.*;
import java.util.concurrent.*;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

public class RequestMaker {
    static int numThreads = 20;

    private String makeRequest (String xml){
        System.out.println("start");
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.add("X-EBAY-SOA-SERVICE-NAME", "FindingService");
        headers.add("X-EBAY-SOA-OPERATION-NAME", "findItemsByKeywords");
        headers.add("X-EBAY-SOA-SECURITY-APPNAME", "key");
        headers.add("Content-Type", "text/xml");
        HttpEntity<String> request = new HttpEntity<String>(xml, headers);
        System.out.println("start");
        ResponseEntity<String> response = restTemplate.postForEntity
                ("http://svcs.ebay.com/services/search/FindingService/v1",
                        request, String.class);
        return response.toString();
    }

    public String request(String xmls) throws Exception {
        List<Future<String>> results = new LinkedList<>();
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        for (String i: xmls.split("REQUEST")) {
            Callable<String> task = () -> {
                String res = makeRequest(i);
                return res;
            };
            results.add(executor.submit(task));
        }
        String res = "";
        for (Future<String> result : results)
            res += result.get();
        System.out.println(res);
        return res;
    }
}