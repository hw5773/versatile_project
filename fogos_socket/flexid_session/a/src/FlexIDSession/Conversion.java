package FlexIDSession;

public class Conversion {
	// for length 2 byte array
	public static int byteArrayToInt(byte[] b) {
	    return  (b[1] & 0xFF) |
	            (b[0] & 0xFF) << 8;
	}
	
	public static byte[] intToByteArray(int a) {
		return new byte[] {
				(byte) ((a >> 8) & 0xFF),
				(byte) (a & 0xFF)
		};
	}
	
	public static void byteToAscii(byte[] b) {
		System.out.print("[Ascii format] ");
		for(int i=0; i<b.length; i++) {
			System.out.print((int)b[i] + " ");
		}
		System.out.println();
	}
	public static void printString(byte[] b) {
		System.out.print("Text [String format]: ");
		String str = new String(b);
		System.out.println(str);
	}

}
