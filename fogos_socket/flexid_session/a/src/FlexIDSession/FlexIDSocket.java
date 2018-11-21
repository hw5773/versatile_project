package FlexIDSession;

import java.io.*;
import java.net.*;

public class FlexIDSocket {
	private Socket socket;

	private DataInputStream dIn;
	private DataOutputStream dOut;

	public String FlexIDToIPAddress(FlexID address) {
		String addr = "127.0.0.1"; // Get the IP address from a FlexIDManager.
		return addr;
	}
	public FlexIDSocket(FlexID address, int port) {
		try {
			// convert FlexID to IP address.
			String IP_addr = FlexIDToIPAddress(address);
			
			socket = new Socket(IP_addr, port);
			
			dIn = new DataInputStream(socket.getInputStream());
			dOut = new DataOutputStream(socket.getOutputStream());

			
		} catch(Exception e) {
			e.printStackTrace();
		}	
	}

	public byte[] read() {
		try {
			int length = dIn.readInt();
			if(length > 0) {
				byte[] msg = new byte[length];
				dIn.readFully(msg, 0, msg.length);
				return msg;
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}
	public void write(byte[] msg) {
		try {
			dOut.writeInt(msg.length);
			dOut.write(msg);
			dOut.flush();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	public InputStream getInputStream() {
		try {
			return socket.getInputStream();
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}
	public OutputStream getOutputStream() {
		try {
			return socket.getOutputStream();
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}
	public void bind(SocketAddress bindpoint) {
		try {
			socket.bind(bindpoint);
		} catch(Exception e) {
			e.printStackTrace();
		}
	}
	public void close() {
		try {
			socket.close();
		} catch(Exception e) {
			e.printStackTrace();
		}
	}
	public void connect(SocketAddress endpoint) {
		try {
			socket.connect(endpoint);
		} catch(Exception e) {
			e.printStackTrace();
		}
	}

}
