package brainfuck.java;

import java.io.File;
import java.util.Scanner;
import java.util.regex.Pattern;

public class BFFile {
    private String inputFile;
    private int[] indexes;
    private int length;
    private int pointer;

    public BFFile(String file) {
        this.pointer = 0;
        if (! this.loadFile(file)) {
            System.exit(1);
        }
        this.concatFile();
    }

    public char getChar() {
        return inputFile.charAt(pointer);
    }

    public void movePointer(int distance) {
        pointer += distance;
    }

    public int getOffset() {
        return indexes[pointer];
    }

    public boolean isEnd() {
        return pointer == inputFile.length();
    }

    private void concatFile() {
        inputFile = inputFile.replace("[-]", "!");
        this.length = inputFile.length();
        indexes = new int[length];
        for (int i = 0; i < length; i++) {
            if (inputFile.charAt(i) == '[') {
                for (int j = i, counter = 0; j < length; j++) {
                    if (inputFile.charAt(j) == '[') {
                        counter++;
                    } else if (inputFile.charAt(j) == ']') {
                        if (counter == 1) {
                            indexes[i] = j - i;
                            indexes[j] = j - i;
                            break;
                        } else {
                            counter--;
                        }
                    }
                }
            }
            if (inputFile.charAt(i) == '+' ||
                    inputFile.charAt(i) == '-' ||
                    inputFile.charAt(i) == '<' ||
                    inputFile.charAt(i) == '>')
            {
                char c = inputFile.charAt(i);
                for (int j = i; j < length; j++) {
                    if (inputFile.charAt(j) != c) {
                        indexes[i] = j - i;
                        break;
                    }
                }
            }
        }
    }

    private boolean loadFile(String file) {
        try {
            Scanner in = new Scanner(new File(file));
            inputFile = in.next();
            while (in.hasNext()) {
                inputFile = inputFile + in.next();
            }
            in.close();
            inputFile = inputFile.replaceAll("[^\\Q[].,<>+-\\E]", "");
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
