package FlexIDSession;

import java.io.DataOutputStream;
import java.io.Serializable;
import java.util.Arrays;
import java.net.*;

/**
 * FlexID socket 占쎄쉭占쎈�∽옙�뵠 占쎌�筌욑옙占쎈┷占쎈뮉 占쎈짗占쎈툧占쎌벥 context 占쎌젟癰귨옙 占쎄깻占쎌삋占쎈뮞
 * @author mckwak
 */
public class FlexIDSession implements Serializable {
	// mckwak: getter/setter, Serializable interface 占쎈막占쎈뼣
	private static final long serialVersionUID = 1L;
	private static final int port = 7780;
	int lock = 0;

	private FlexID SFID; // source FlexID
	private FlexID DFID; // destination FlexID
	private byte[] connID;
	
//	private int sentBytes;	// sent data's seq #
//	private int sentAck;	// sent ack #
//	private int recvBytes;	// received data's seq #
//	private int recvAck;	// received ack #
	
	// managed at the inbound, outbound function.
	private int SEQ;	
	private int ACK;	
	
	private CircularQueue rbuf;
	private CircularQueue wbuf;

	FlexIDSocket socket;
	private Thread inThread;
	private Thread outThread;
	
	public FlexIDSession(FlexID sFID, FlexID dFID, FlexIDSocket sock) {
		SFID = sFID;
		DFID = dFID;
		connID = new byte[20]; // TODO: Generate with FlexIDs.
//		recvBytes = 0;
//		recvAck = 0;
//		sentBytes = 0;
//		sentAck = 0;
		SEQ = 0;
		ACK = 0;
		
		rbuf = new CircularQueue();
		wbuf = new CircularQueue();
		if(sock != null)
			socket = sock;
		else
			socket = new FlexIDSocket(DFID, port); // TODO: Get port #
		
		inThread = new Thread(new inbound());
		inThread.setDaemon(true);
		inThread.start();
		
		outThread = new Thread(new outbound());
		outThread.setDaemon(true);
		outThread.start();
	}
	public FlexIDSession(FlexID sFID, FlexID dFID) {
		this(sFID, dFID, null);
	}
	public static FlexIDSession accept() {
		FlexIDServerSocket server = new FlexIDServerSocket(port);
		System.out.println("Server waits a connections.");
		FlexIDSocket sock = server.accept();
		if(sock == null) {
			System.out.println("accept failed.");
			return null;
		}
		
		System.out.println("Connected.");
		FlexID sFID = new FlexID();
		FlexID dFID = new FlexID();
		
		return new FlexIDSession(sFID, dFID, sock);
	}

	// Application send
	public void send(byte[] msg) {
		while(lock == 1) {
		}
		lock = 1;
		wbuf.write(msg);
		lock = 0;
	}
	// Application receive
	public byte[] receive() {
		while(lock != 1) {}
		lock = 1;
		byte[] result = rbuf.read(2048);
		lock = 0;
		return result;
	}
	
	// Check wbuf to send msg to socket.
	public int checkMsgToSend() {
		if(wbuf.isEmpty(1)) {
			return -1;
		}
		else return 1;
	}
	
	// Polling: To get msg from socket. Then write to the rbuf.
	public byte[] getRecvMsg() {
		try {
			byte[] message = socket.read(); // is it block?
			
			if(message != null) return message;
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		return null;
	}
	
	private class inbound implements Runnable {
		public void run() {
			try {
				while(!inThread.isInterrupted()) {
					//checkAddress();	// TODO
					byte[] message;
					if((message = getRecvMsg()) != null && (lock == 0)) {
						lock = 1;
						
						byte[] header = getHeader(message); // length(2B) + connID(20B) + seq(4B), ack(4B)
						byte[] data = getData(message);
						byte[] msgConnID = Arrays.copyOfRange(header, 2, 21);
						
						if(connID != msgConnID) {
							System.out.println("connID unmatched.");
							continue;
						}
						
						int length = Conversion.byteArrayToInt(Arrays.copyOfRange(header, 0, 1)); // total length
						int msgSeq = Conversion.byteArrayToInt(Arrays.copyOfRange(header, 22, 25));
						int msgAck = Conversion.byteArrayToInt(Arrays.copyOfRange(header, 26, 29));
						
						if(length > 30) { // received data message.
							if(ACK < msgSeq) {
								ACK = msgSeq+1;
								rbuf.write(data);
								
								// send ACK message.
								byte[] ACKheader = setHeader(null);
								byte[] ACKmessage = new byte[30];
								System.arraycopy(ACKheader, 0, ACKmessage, 0, 30);
								socket.write(ACKheader);
							}
						}
						else { // received ACK message.
							if(msgAck != (SEQ+1)) {
								System.out.println("ACK number error!");
								break;
							}
						}
					}
				}
			} catch (Exception e) {
				e.printStackTrace();
			} finally {
				lock = 0;
			}

			System.out.println("inThread done.");
		}
	}
		
	private class outbound implements Runnable {
		public void run() {
			try {
				while(!outThread.isInterrupted()) {
					//checkAddress();	// TODO
					
					if(checkMsgToSend() == 1 && (lock == 0)) {
						lock = 1;
						System.out.println("send wbuf msg to socket");
						byte[] data = wbuf.read(2048);
						byte[] header = setHeader(data);
						byte[] message = new byte[30 + data.length];
						
						System.arraycopy(header, 0, message, 0, 30);
						System.arraycopy(data, 0, message, 30, data.length);
						System.out.println("MSG: ");
						Conversion.byteToAscii(message);
						socket.write(message);
					}
					// TODO: get data from wbuf, add header, send to socket, change sentAck/sentSEQ.
				}
			} catch (Exception e) {
				e.printStackTrace();
			} finally {
				lock = 0;
			}
			
			System.out.println("outThread done.");
		}
	}
	
	public byte[] getHeader(byte[] message) {
		return Arrays.copyOfRange(message, 0, 30);
	}
	public byte[] getData(byte[] message) {
		int length = Conversion.byteArrayToInt(Arrays.copyOfRange(message, 0, 1));
		byte[] data = new byte[length];
		System.arraycopy(message, 30, data, 0, length); // 30: header size
		return data;
	}
	public byte[] setHeader(byte[] message) {
		try {
			// Header(30) = length(2B) + connID(20B) + seq(4B), ack(4B)
			byte[] length = new byte[2];
			byte[] seq = new byte[4];
			byte[] ack = new byte[4];
			byte[] header = new byte[30];
			
			int msgLength;
			
			if(message == null) { // ack 
				msgLength = 30;
				ack = String.valueOf(ACK).getBytes("UTF-8");
			}
			else { // data
				msgLength = message.length + 30;
				SEQ += (msgLength - 30);
				byte[] temp = String.valueOf(SEQ).getBytes("UTF-8");
				System.arraycopy(temp, 0, seq, 0, temp.length);
			}
			
			length = Conversion.int32ToByteArray(msgLength);
			System.arraycopy(length, 0, header, 0, 2);
			System.arraycopy(connID, 0, header, 2, 20);
			System.arraycopy(seq, 0, header, 22, 4);
			System.arraycopy(ack, 0, header, 26, 4);
			
			System.out.println("header: ");
			Conversion.byteToAscii(header);
			
			return header;
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		return null;
	}
	
	public void close() {
		socket.close();
	}
	public FlexID getSFID() {
		return SFID;
	}
	public void setSFID(FlexID sFID) {
		SFID = sFID;
	}
	public FlexID getDFID() {
		return DFID;
	}
	public void setDFID(FlexID dFID) {
		DFID = dFID;
	}
}


