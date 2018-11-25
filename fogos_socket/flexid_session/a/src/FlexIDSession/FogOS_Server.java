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
				byte[] msg = new byte[2048];
				int msgLen;
				if((msgLen = FS1.receive(msg)) > 0) {
					System.out.println("[Server] Received message size: " + msgLen);
//					Conversion.byteToAscii(msg, msgLen);
				}
//				Thread.sleep(2000);
			}
			
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(0);
		} finally {
			FS1.close();
		}
	}
}
