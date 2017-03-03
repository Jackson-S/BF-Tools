package brainfuck.java;

public class BFTape {
    private int pointer;
    private int[] tapeRoll;

    public BFTape(int tapeSize) {
        this.pointer = 0;
        this.tapeRoll = new int[tapeSize];
    }

    public int getCurrent() {
        return tapeRoll[pointer];
    }

    public void zero() {
        tapeRoll[pointer] = 0;
    }

    public void add(int c) {
        tapeRoll[pointer] += c;
    }

    public void sub(int c) {
        tapeRoll[pointer] -= c;
    }

    public void left(int c) {
        pointer -= c;
    }

    public void right(int c) {
        pointer += c;
    }

    void print() {
        System.out.print((char) tapeRoll[pointer]);
        System.out.flush();
    }
}
