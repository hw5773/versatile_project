package FlexIDSession;

import java.nio.ByteBuffer;

public class Conversion {
	// for length 2 byte array
	public static int byteArrayToInt(byte[] b) {
	    return  (b[1] & 0xFF) |
	            (b[0] & 0xFF) << 8;
	}
	
	public static byte[] int16ToByteArray(int a) {
		return new byte[] {
				(byte) ((a >> 8) & 0xFF),
				(byte) (a & 0xFF)
		};
	}
	
	public static void byteToAscii(byte[] b) {
		System.out.print("[Ascii]	");
		for(int i=0; i<b.length; i++) {
			System.out.print((int)b[i] + " ");
			if((i+1) % 10 == 0) {
				System.out.println();
				System.out.print("	");
			}
		}
		System.out.println();
	}
	public static byte[] int32ToByteArray(int num) {
		byte[] bytes = ByteBuffer.allocate(2).putInt(num).array();
		return bytes;
	}
	public static void printString(byte[] b) {
		System.out.print("Text [String format]: ");
		String str = new String(b);
		System.out.println(str);
	}

}
