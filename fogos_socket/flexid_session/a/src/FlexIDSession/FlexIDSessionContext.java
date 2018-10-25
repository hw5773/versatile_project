package FlexIDSession;

import java.io.Serializable;

/**
 * FlexID socket 세션이 유지되는 동안의 context 정보 클래스
 * @author mckwak
 */
public class FlexIDSessionContext implements Serializable {
	// mckwak: getter/setter, Serializable interface 할당
	private static final long serialVersionUID = 1L;
	int length;
	FlexID SFID; // source FlexID
	FlexID DFID; // destination FlexID
	int lastSeq;
	int lastAck;
	byte[] rbuf, wbuf; // make it with a circular queue

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


