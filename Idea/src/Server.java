import java.net.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
public class Server {
    public static void main(String[] args) throws IOException {
        ServerSocket serverSocket = null;

        try {
            serverSocket = new ServerSocket(9090);
        } catch (IOException ex) {
            System.out.println("Can't setup server on this port number. ");
        }

        while(true)
        {
            Socket socket = serverSocket.accept();
            InputStream in = socket.getInputStream();

            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            byte buffer[] = new byte[1024*1024];
            for(int s; (s=in.read(buffer)) != -1; )
            {
                baos.write(buffer, 0, s);
            }
            byte result[] = baos.toByteArray();
            String str = new String(result, StandardCharsets.UTF_8);
            RequestMaker rm = new RequestMaker();
            try {
                rm.request(str);
            }
            catch (Exception e)
            {
            }
        }

    }
}