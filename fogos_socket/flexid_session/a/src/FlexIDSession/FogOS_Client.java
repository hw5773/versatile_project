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

			int i=1;
			while(true) {
				if(FS1.send(message) > 0) i++;
				if(i >= 200) break;
				if(i%10 == 0) Thread.sleep(1000);
			}
			System.out.println("done");
			Thread.sleep(1000000);
			
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			FS1.close();
		}
	}
}
