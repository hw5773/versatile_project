package FlexIDSession;

import java.io.*;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;


public class FogOS_Client {

	public static void main(String[] args) {
		FlexID SFID = new FlexID();
		FlexID DFID = new FlexID();
		System.out.println("Client connects to the server.");
		FlexIDSession FS1 = new FlexIDSession(SFID, DFID);
		//DataOutputStream dOut = new DataOutputStream(socket.getOutputStream());
		
		try {
			System.out.println("Client sends a message to the server");
			byte[] message = "Hello".getBytes(); // TODO: define message format.
			FS1.send(message);
			Thread.sleep(5000);
//			dOut.writeInt(message.length);
//			dOut.write(message);
//			dOut.flush();
			byte[] message2 = "Welcome".getBytes();
			FS1.send(message2);
			Thread.sleep(100000);
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			FS1.close();
		}
	}
}
