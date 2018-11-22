package FlexIDSession;

import java.util.Arrays;

public class CircularQueue {
	private int currentSize;
	private int front;
	private int rear;
	private int maxSize;
	private byte[] queueArray;
	
	public CircularQueue(int maxSize) {
		this.currentSize = 0;
		this.front = -1;
		this.rear = -1;
		
		this.maxSize = maxSize;
		this.queueArray = new byte[this.maxSize];
	}
	
	public CircularQueue() {
		this(100000000);
	}
	
	public boolean isEmpty(int size) {
		return (currentSize - size < 0);
	}
	
	public boolean isFull(int size) {
		return (currentSize + size > this.maxSize);
	}
	
	public void write(byte[] item) {
		System.out.print("item: ");
		Conversion.byteToAscii(item);
		if(isFull(item.length)) throw new ArrayIndexOutOfBoundsException();
		else {
			int readFrom = 0;
			int readLen = item.length;
			
			rear = (rear + 1) % this.maxSize;
			if((rear+item.length) >= this.maxSize) {
				System.arraycopy(item, 0, queueArray, rear, (this.maxSize-rear));
				
				readFrom = this.maxSize-rear;
				readLen = item.length - (this.maxSize-rear);
				rear = 0;
			}
						
			System.arraycopy(item, readFrom, queueArray, rear, readLen);
			rear = (rear + readLen - 1) % this.maxSize;
			currentSize += item.length;
			if(front == -1) {
				front = 0;
			}
		}
		System.out.println("written queueArray: ");
		Conversion.byteToAscii(queueArray);
		try {
			Thread.sleep(10000);
		} catch (Exception e) {
			
		}
	}
		
	public byte[] read(int size) {
		byte[] item;
		
		if(currentSize < size) {
			size = currentSize;
		}
		item = new byte[size];
		
		System.out.println("front: " + front);
		System.out.println("rear: " + rear);
		
		if(size == 0) {
			return null;
		}
		else {
			int writeFrom = 0;
			int writeLen = size;
			
			if((front+size) > this.maxSize) {
				System.arraycopy(queueArray, front, item, 0, (this.maxSize-front));
				
				writeFrom = this.maxSize-front;
				writeLen = size - (this.maxSize-front);
				Arrays.fill(queueArray,  front, front+(this.maxSize-front), (byte) 0);
				front = 0;
			}
			System.out.println("queueArray: ");
			Conversion.byteToAscii(queueArray);
			System.arraycopy(queueArray, front, item, writeFrom, writeLen);
			Arrays.fill(queueArray, front, front+size, (byte) 0);
			front = (front + writeLen) % this.maxSize;
			
			currentSize -= size;
			
			System.out.println("item: ");
			Conversion.byteToAscii(item);
			return item;
		}
	}
}
