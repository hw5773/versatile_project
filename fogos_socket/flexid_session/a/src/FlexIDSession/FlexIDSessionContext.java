package FlexIDSession;

public class FlexIDSessionContext {
	int length;
	FlexID SFID; // source FlexID
	FlexID DFID; // destination FlexID
	int lastSeq;
	int lastAck;
	byte[] rbuf, wbuf; // make it with a circular queue
}


