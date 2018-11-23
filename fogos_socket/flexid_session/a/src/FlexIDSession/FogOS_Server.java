package FlexIDSession;

import java.io.*;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;


public class FogOS_Server {

	public static void printString(byte[] b) {
		System.out.print("Text [String format]: ");
		String str = new String(b);
		System.out.println(str);
	}
	
	public static void main(String[] args) {
		FlexIDSession FS1 = FlexIDSession.accept();;
		try {
			if(FS1 == null) {
				System.out.println("Server failed.");
				System.exit(0);
			}
			
			while(true) {
				byte[] msg = FS1.receive();
				if(msg != null) {
					System.out.println("[Server] Received message: ");
					Conversion.byteToAscii(msg);
				}
				Thread.sleep(1000);
				System.out.println("wake up");
			}
			
//			int length = dIn.readInt();
//			System.out.println("length: " + length);
//			System.out.println("receiving a message.");
//			if(length>0) {
//				byte[] message = new byte[length];
//				dIn.readFully(message, 0, message.length);
//				printString(message);
//				Conversion.byteToAscii(message);
//			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			FS1.close();
		}
	}
}
