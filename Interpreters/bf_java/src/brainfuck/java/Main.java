package brainfuck.java;

public class Main {
    public static void main(String[] args) {
	    BFFile file = new BFFile(args[0]);
	    BFTape tape = new BFTape(30000);
	    while (! file.isEnd()) {
	        switch(file.getChar()) {
                case '[':
                    if (tape.getCurrent() == 0) {
                        file.movePointer(file.getOffset() + 1);
                    } else {
                        file.movePointer(1);
                    }
                    break;
                case ']':
                    if (tape.getCurrent() == 0) {
                        file.movePointer(1);
                    } else {
                        file.movePointer(0 - (file.getOffset()) + 1);
                    }
                    break;
                case '+':
                    tape.add(file.getOffset());
                    file.movePointer(file.getOffset());
                    break;
                case '-':
                    tape.sub(file.getOffset());
                    file.movePointer(file.getOffset());
                    break;
                case '<':
                    tape.left(file.getOffset());
                    file.movePointer(file.getOffset());
                    break;
                case '>':
                    tape.right(file.getOffset());
                    file.movePointer(file.getOffset());
                    break;
                case '.':
                    tape.print();
                    file.movePointer(1);
                    break;
                case '!':
                    tape.zero();
                    file.movePointer(1);
                    break;
                default:
                    file.movePointer(1);
                    break;
            }
        }
    }
}
