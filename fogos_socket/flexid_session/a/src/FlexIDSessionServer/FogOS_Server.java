package FlexIDSessionServer;

import java.io.*;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;


public class FogOS_Server {
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
		
		FlexID my = new FlexID();
		FlexID peer = new FlexID();	
				
		FlexIDServerSocket server = new FlexIDServerSocket(7779);
		System.out.println("Server waits a connections.");
		FlexIDSocket socket = server.accept();
		System.out.println("Connected.");
		

		/* Session Management */
		DataInputStream dIn = new DataInputStream(socket.getInputStream());
		try {
			int length = dIn.readInt();
			System.out.println("length: " + length);
			System.out.println("receiving a message.");
			if(length>0) {
				byte[] message = new byte[length];
				dIn.readFully(message, 0, message.length);
				printString(message);
				byteToAscii(message);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
