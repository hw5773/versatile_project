package FlexIDSessionClient;

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
	
	public static void main(String[] args) {
		
		FlexID DFID = new FlexID();
		System.out.println("Client connects to a server.");
		FlexIDSocket socket = new FlexIDSocket(DFID, 7779);
		DataOutputStream dOut = new DataOutputStream(socket.getOutputStream());
		
		try {
			byte[] message = "Hello".getBytes();
			dOut.writeInt(message.length);
			dOut.write(message);
			dOut.flush();
		} catch (Exception e) {
			e.printStackTrace();
		}
		

		/* Session Management */
		
		}
}
