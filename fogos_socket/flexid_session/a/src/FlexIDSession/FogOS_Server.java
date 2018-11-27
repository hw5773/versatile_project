package FlexIDSession;

import java.io.*;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;


public class FogOS_Server {
	public static void main(String[] args) {
		FlexIDSession FS1 = FlexIDSession.accept();;
		try {
			if(FS1 == null) {
				System.out.println("Server failed.");
				System.exit(0);
			}
			
			System.out.println("Server sends a message to the client.");
			
			int dataSize = 10000;
			int i = 0;
			
			System.out.println("Server sends a entire data size to the client.");
			FS1.send(Conversion.int32ToByteArray(dataSize));
			byte[] message = "a".getBytes();
			while(true) {
				if(FS1.send(message) > 0) // always true unless it exceeds server's wbuf size 
					i++;
				if(i >= dataSize) break;
			}
			
			System.out.println("done");
			Thread.sleep(1000000);
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(0);
		} finally {
			FS1.close();
		}
	}
}
