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

	int length;
	FlexID SFID; // source FlexID
	FlexID DFID; // destination FlexID
	int lastSeq;
	int lastAck;
	byte[] rbuf, wbuf; // make it with a circular queue

	public FlexIDSessionContext() {
		super();
		this.rbuf = new byte[BUF_SIZE];
		this.wbuf = new byte[BUF_SIZE];
	}
	
	Object readBuf(int bytes) {
		byte[] readBytes = rbuf;
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
	
	void writeBuf(Object o) {
		ByteArrayOutputStream bos = new ByteArrayOutputStream();
		ObjectOutput out = null;
		try {
		  out = new ObjectOutputStream(bos);   
		  out.writeObject(o);
		  out.flush();
		  wbuf = bos.toByteArray();
		  bos.close();
		} catch (IOException ex) {}
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
		return rbuf;
	}
	public void setRbuf(byte[] rbuf) {
		this.rbuf = rbuf;
	}
	public byte[] getWbuf() {
		return wbuf;
	}
	public void setWbuf(byte[] wbuf) {
		this.wbuf = wbuf;
	}
}


