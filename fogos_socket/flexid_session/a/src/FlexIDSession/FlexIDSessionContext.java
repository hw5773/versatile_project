package FlexIDSession;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectInput;
import java.io.ObjectInputStream;
import java.io.ObjectOutput;
import java.io.ObjectOutputStream;

/**
 * FlexID socket 세션이 유지되는 동안의 context 정보 클래스
 * @author mckwak
 */
public class FlexIDSessionContext {
	public static final int BUF_SIZE = 1024;   
	int rBuffHead, wBuffHead;
	int length;
	FlexID SFID; // source FlexID
	FlexID DFID; // destination FlexID
	int lastSeq;
	int lastAck;
	byte[] rbuff, wbuff; // make it with a circular queue

	public FlexIDSessionContext() {
		super();
		this.rbuff = new byte[BUF_SIZE];
		this.wbuff = new byte[BUF_SIZE];
		this.rBuffHead = 0;
		this.wBuffHead = 0;
	}
	
	Object read(int bytes) {
		byte[] readBytes = rbuff;
		ByteArrayInputStream bis = new ByteArrayInputStream(readBytes);
		ObjectInput in = null;
		try {
		  in = new ObjectInputStream(bis);
		  Object o = in.readObject();
	      if (in != null) in.close();
		  return o;
		} catch (IOException ex) {}
		catch (ClassNotFoundException e) {}
		return null;
 	}
	
	void write(Object o) {
		ByteArrayOutputStream bos = new ByteArrayOutputStream();
		ObjectOutput out = null;
		try {
		  out = new ObjectOutputStream(bos);   
		  out.writeObject(o);
		  out.flush();
		  wbuff = bos.toByteArray();
		  bos.close();
		} catch (IOException ex) {}
	}
	
	int readBuff(byte[] dataToRead, int startIdx, int endIdx) {
		int readBytes = 0;
		return readBytes;
	}

	int writeBuff(byte[] dataToWrite) {
		int writeBytes = 0;
		return writeBytes;
	}

	public int getLength() {
		return length;
	}
	public void setLength(int length) {
		this.length = length;
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
	public int getLastSeq() {
		return lastSeq;
	}
	public void setLastSeq(int lastSeq) {
		this.lastSeq = lastSeq;
	}
	public int getLastAck() {
		return lastAck;
	}
	public void setLastAck(int lastAck) {
		this.lastAck = lastAck;
	}
	public byte[] getRbuf() {
		return rbuff;
	}
	public void setRbuf(byte[] rbuf) {
		this.rbuff = rbuf;
	}
	public byte[] getWbuf() {
		return wbuff;
	}
	public void setWbuf(byte[] wbuf) {
		this.wbuff = wbuf;
	}
}


