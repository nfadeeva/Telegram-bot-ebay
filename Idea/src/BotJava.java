import java.util.*;
import java.util.concurrent.*;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class BotJava {

    public static String readFile(String filename) throws Exception
    {
        String content = null;
        File file = new File(filename); //for ex foo.txt
        FileReader reader = null;
        try {
            reader = new FileReader(file);
            char[] chars = new char[(int) file.length()];
            reader.read(chars);
            content = new String(chars);
            reader.close();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if(reader !=null){reader.close();}
        }
        return content;
    }
    public static void main(String[] ar){
        RequestMaker requestMaker = new RequestMaker();
        String res = "";
        try {
            res = requestMaker.request(readFile("/home/fadnastya/PycharmProjects/Telegram-bot-ebay/text.txt"));
        }
        catch (Exception e) {
            
        }
        System.out.println(res);

    }
}