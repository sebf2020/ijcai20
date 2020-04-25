import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class Client {

    public String extendData;

    public Client(String extendData){
        this.extendData = extendData;
    }

    public String connectOracle(){
        String re = "";
        InputStream is = null;
        DataInputStream dis = null;
        OutputStream outputStream = null;
        DataOutputStream dos = null;
        try {
            Socket client = new Socket("127.0.0.1",8888);
            is = client.getInputStream();
            dis = new DataInputStream(is);
            outputStream = client.getOutputStream();
            dos = new DataOutputStream(outputStream);

            String tempString = extendData;
            dos.writeUTF(tempString);
            re = dis.readUTF();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (dos != null){
                try {
                    dos.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            if (outputStream != null){
                try {
                    outputStream.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return re;
    }
}
