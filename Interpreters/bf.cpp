#include <iostream>
#include <string>
#include <regex>
#include <fstream>
#include <unistd.h>

using namespace std;

class BFTape {
private:
    int pointer;
    int *tapeRoll;
    
public:
    BFTape(int tapeSize) {
        pointer = 0;
        tapeRoll = new int[tapeSize];
    }
    ~BFTape() { free(tapeRoll); }
    char getCurrent() { return tapeRoll[pointer]; }
    void zero() { tapeRoll[pointer] = 0; }
    void add(int c) { tapeRoll[pointer] += c; }
    void sub(int c) { tapeRoll[pointer] -= c; }
    void left(int c) { pointer -= c; }
    void right(int c) { pointer += c; }
    void print() {
        cout << (char) tapeRoll[pointer];
        cout.flush();
    }
};

class BFFile {
private:
    string inputFile;
    int *indexes;
    int length;
    int pointer;
    
public:
    BFFile(string file) {
        pointer = 0;
        loadFile(file);
        concatFile();
    }
    ~BFFile() { free(indexes); }
    char getChar() { return inputFile[pointer]; }
    void movePointer(int distance) { pointer += distance; }
    int getOffset() { return indexes[pointer]; }
    bool isEnd() { return pointer >= inputFile.length(); }
    
private:
    void concatFile() {
        regex rx("\\[-\\]");
        inputFile = regex_replace(inputFile, rx, "!");
        length = (int) inputFile.length();
        indexes = new int[length];
        for (int i = 0; i < length; i++) {
            if (inputFile[i] == '[') {
                for (int j = i, counter = 0; j < length; j++) {
                    if (inputFile[j] == '[') {
                        counter++;
                    } else if (inputFile[j] == ']') {
                        if (counter == 1) {
                            indexes[i] = indexes[j] = j - i;
                            break;
                        } else {
                            counter--;
                        }
                    }
                }
            }
            if (inputFile[i] == '+' or
                inputFile[i] == '-' or
                inputFile[i] == '<' or
                inputFile[i] == '>')
            {
                char c = inputFile[i];
                for (int j = i; j < length; j++) {
                    if (inputFile[j] != c) {
                        indexes[i] = j - i;
                        break;
                    }
                }
            }
        }
    }
    
    bool loadFile(string file) {
        fstream read(file);
        if (! read.is_open()) { return false; }
        char c;
        for (int i = 0; ! read.eof(); i++) {
            read.get(c);
            inputFile += c;
        }
        read.close();
        return true;
    }
};

int main(int argc, char** argv) {
    if (argc == 1) {
        cout << "Usage: " << argv[0] << " filename.b" << endl;
        return 1;
    } else if (access(argv[1], R_OK) == -1) {
        cout << "File name incorrect or no read permissions." << endl;
        return 1;
    }
    
    BFFile file = BFFile(string(argv[1]));
    BFTape tape = BFTape(30000);
    
    while(! file.isEnd()) {
        switch(file.getChar()) {
            case '>':
                tape.right(file.getOffset());
                file.movePointer(file.getOffset());
                break;
                
            case '+':
                tape.add(file.getOffset());
                file.movePointer(file.getOffset());
                break;
                
            case '<':
                tape.left(file.getOffset());
                file.movePointer(file.getOffset());
                break;
                
            case ']':
                if (tape.getCurrent()) {
                    file.movePointer(1 - file.getOffset());
                } else {
                    file.movePointer(1);
                }
                break;
                
            case '-':
                tape.sub(file.getOffset());
                file.movePointer(file.getOffset());
                break;
                
            case '!':
                tape.zero();
                file.movePointer(1);
                break;
                
            case '[':
                if (! tape.getCurrent()) {
                    file.movePointer(file.getOffset() + 1);
                } else {
                    file.movePointer(1);
                }
                break;
                
            case '.':
                tape.print();
                file.movePointer(1);
                break;
                
            default:
                file.movePointer(1);
                break;
        }
    }
}
