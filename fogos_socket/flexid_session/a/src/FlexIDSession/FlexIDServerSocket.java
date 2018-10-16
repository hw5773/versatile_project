package FlexIDSession;

import java.io.*;
import java.net.*;

public class FlexIDServerSocket {
	private ServerSocket server;
	private FlexIDSessionContext context;
	FlexIDServerSocket() {
		try {
			server = new ServerSocket();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	FlexIDServerSocket(int port) {
		try {
			server = new ServerSocket(port);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	String FlexIDToIPAddress(FlexID address) {
		String addr = "127.0.0.1"; // Get the IP address from a FlexIDManager.
		return addr;
	}
	FlexIDSocket accept() {
		Socket sock = new Socket();
		try {
			sock = server.accept();
		} catch (Exception e) {
			e.printStackTrace();
		}
		FlexIDSocket socket = new FlexIDSocket(sock);
		return socket;
	}
	void bind(SocketAddress bindpoint) {
		try {
			server.bind(bindpoint);
		} catch(Exception e) {
			e.printStackTrace();
		}
	}
	void close() {
		try {
			server.close();
		} catch(Exception e) {
			e.printStackTrace();
		}
	}
}
