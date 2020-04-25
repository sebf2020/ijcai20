package connection;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.sql.*;

public class OracleMachine {
    Connection c;
    private OracleMachine(String databaseName,String user,String password){
        try {
            Class.forName("com.mysql.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
        try {
            c = DriverManager.getConnection(String.format("jdbc:mysql://localhost:3306/%s?characterEncoding=utf8&useSeverPrepStmits",databaseName),user,password);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
    public Connection getConnection(){
        return c;
    }


    public static void main(String[] args) throws SQLException{

        OracleMachine server = new OracleMachine("socket","root","admin");
        PreparedStatement ps = server.getConnection().prepareStatement("select * from script where receive=?");

        InputStream is = null;
        DataInputStream dis = null;
        OutputStream os = null;
        DataOutputStream dos = null;
        try {
            ServerSocket serverSocket = new ServerSocket(8888);
            while (true){
                Socket socket = serverSocket.accept();
                is = socket.getInputStream();
                dis = new DataInputStream(is);
                os = socket.getOutputStream();
                dos = new DataOutputStream(os);
                String s;
                //结束标识符以单个#结束
                while (!(s = dis.readUTF()).equals("#")){
                    ps.setString(1,s);
                    ResultSet resultSet = ps.executeQuery();
                    if (resultSet.next()){
                        String result = ExcuteScript.excute(resultSet.getString("Script"));
                        dos.writeUTF(result);
                    }
                    else {
                        dos.writeUTF("error");
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (dis != null){
                try {
                    dis.close();
                } catch (IOException e){
                    e.printStackTrace();
                }
            }
            if (is != null){
                try {
                    is.close();
                } catch (IOException e){
                    e.printStackTrace();
                }
            }
        }

    }
}