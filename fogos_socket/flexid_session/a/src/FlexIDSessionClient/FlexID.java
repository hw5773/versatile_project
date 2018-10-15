package FlexIDSessionClient;

public class FlexID {
	byte[] id;
	int type; // Content, Service, ... (predefined)
	FlexIDInfo info; // Attribute-Value-Pairs
	Locator loc; // TCPIPAddress, ... (Parent-Child)
		
}
