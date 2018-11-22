package FlexIDSession;

import java.io.*;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;


public class FogOS_Client {
	public static void byteToAscii(byte[] b) {
		System.out.print("Text [Ascii format]: ");
		for(int i=0; i<b.length; i++) {
			System.out.print((int)b[i] + " ");
		}
		System.out.println();
	}
	public static void printString(byte[] b) {
		System.out.print("Text [String format]: ");
		String str = new String(b);
		System.out.println(str);
	}
	
//	public static void main(String[] args) {
//		FlexID SFID = new FlexID();
//		FlexID DFID = new FlexID();
//		System.out.println("Client connects to a server.");
//		FlexIDSession FS1 = new FlexIDSession(SFID, DFID);
//		//DataOutputStream dOut = new DataOutputStream(socket.getOutputStream());
//		
//		try {
//			byte[] message = "Hello".getBytes(); // TODO: define message format.
//			FS1.send(message);
////			dOut.writeInt(message.length);
////			dOut.write(message);
////			dOut.flush();
//		} catch (Exception e) {
//			e.printStackTrace();
//		}
//		
//
//		/* Session Management */
//		
//		}
}
