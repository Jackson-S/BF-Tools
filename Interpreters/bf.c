/* --- bf.c ---
 * Made by Jackson Sommerich - 2017
 *
 * You are free to redistribute this software, but please retain this header
 * in the source, or if closed source please include this header somewhere
 * end-user accessible in its entirety, and notify me when your software is
 * released, that'd be pretty cool of you. Other than that you are free to do
 * with this software as you please.
 */

#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

// Constant Definitions
#define DATASIZE 30000

// Type Definitions
typedef int offset_t;
typedef int_fast8_t data_t;
typedef struct {
  char instruction;
  offset_t offset;
} code_t;

// Prototypes
void generateOffsets(char *in, code_t *out, const size_t length);
void generateSymbols(char *code, const size_t length);
void programLoop(code_t *program, data_t *data, const size_t length);
size_t stripChars(char* program, const size_t length, const char *chars);

int main(int argc, char **argv) {
  if (argc == 1) {
    printf("Usage: %s filename.b\n", argv[0]);
    return 1;
  }
  // Check .b file to interperet is specified and exists
  if (access(argv[1], R_OK) == -1) {
    printf("File name incorrect or no read permissions. Quitting.\n");
    return 1;
  }
  FILE *input_file = fopen(argv[1], "r");
  // Get the length of the program to later create an array of the correct size
  fseek(input_file, 0, SEEK_END);
  size_t programLength = ftell(input_file);
  rewind(input_file);
  // Allocate arrays to store program
  char *program = malloc(programLength * sizeof(char));
  // Read the input file into the program array
  if (fread(program, sizeof(char), programLength, input_file) != programLength) {
    printf("Program cannot read data.\n");
    return 1;
  }
  fclose(input_file);
  // Strip extraneous characters and compress string, function
  // returns length of new string
  programLength = stripChars(program, programLength, "[]<>+-.,");
  generateSymbols(program, programLength);
  programLength = stripChars(program, programLength, "[]<>+-.,$!@#");
  code_t *code = calloc(programLength, sizeof(code_t));
  generateOffsets(program, code, programLength);
  free(program);
  // Run the optomised file
  data_t *data = calloc(DATASIZE, sizeof(data_t));
  programLoop(code, data, programLength);
  // Free pointers
  free(code);
  free(data);
}

/*
* Go through the file tallying up any adjacent symbols, the amount of
* symbols is placed in the offset array at the location of the first
* symbol that occurs.
*/
void generateOffsets(char *in, code_t *out, const size_t length) {
  for (const char *endpoint = in + length; in <= endpoint; in++, out++) {
    if (*in == '[') {
      // Find offsets between loop parenthesis
      int tally = 0;
      for (char *j = in; j <= endpoint; j++) {
        if (*j == '[') { tally++; }
        else if (*j == ']') { tally--; }
        if (tally == 0) {
          out->instruction = *in;
          out->offset = j - in;
          out[out->offset].instruction = ']';
          out[out->offset].offset = -(out->offset);
          break;
        }
      }
    }
    else if (*in == '<' || *in == '>' || *in == '+' || *in == '-') {
      /* Check for repeating sequences, and add the length of that sequence
       * to the offset, on completion skip over the sequence. */
      for (char *j = in; j <= endpoint; j++) {
        if (*j != *in) {
          out->instruction = *in;
          out->offset = j - in;
          out += (out->offset - 1);
          in = (j - 1);
          break;
        }
      }
    }
    // Adds offsets and instructions to non-repeating characters
    else if (*in != ']') {
      out->instruction = *in;
      out->offset = 1;
    }
  }
}

/*
 * Replaces common constructs in the input code with symbols represending
 * a shorthand function, optimising the output code.
 */
void generateSymbols(char *in, const size_t length) {
  char *begin = in;
  for (const char *endpoint = in + length; in <= endpoint; in++) {
    if (! strncmp(in, "<-", 2)) {
      memmove(in, "$0", 2);
      in += 2;
    }
    else if (! strncmp(in, "[-]", 3)) {
      memmove(in, "!00", 3);
      in += 3;
    }
    else if (! strncmp(in, "[->+<]", 6) || ! strncmp(in, "[>+<-]", 6)) {
      memmove(in, "@00000", 6);
      in += 6;
    }
    else if (! strncmp(in, "[-<+>]", 6) || ! strncmp(in, "[<+>-]", 6)) {
      memmove(in, "#00000", 6);
      in += 6;
    }
  }
}

/*
 * Cycles through the program array, running each character
 */
void programLoop(code_t *program, data_t *data, const size_t length) {
  const code_t *programEnd = &program[length];
  while (program < programEnd) {
    switch (program->instruction) {
      case '[':
        if (! data[0]) {
          break;
        } else {
          program += 1;
          continue;
        }

      case ']':
        if (data[0]) {
          break;
        } else {
          program += 1;
          continue;
        }

      case '>':
        data += program->offset;
        break;

      case '<':
        data -= program->offset;
        break;

      case '+':
        data[0] += program->offset;
        break;

      case '-':
        data[0] -= program->offset;
        break;

      case '!':
        data[0] = 0;
        break;

      case '@':
        data[1] += data[0];
        data[0] = 0;
        break;

      case '$':
        data--[-1] -= 1;
        break;

      case '#':
        data[-1] += *data;
        data[0] = 0;
        break;

      case '.':
        putchar(data[0]);
        break;

      case ',':
        data[0] = getc(stdin);
        break;
    }
    program += program->offset;
  }
}

/*
 * Removes any characters not found in filter from the input, returns the new
 * length of the input
 */
size_t stripChars(char* in, const size_t length, const char *filter) {
  size_t result = 0;
  for (int i = 0; i < length; i++) {
    if (strchr(filter, in[i]) != NULL){
      in[result++] = in[i];
    }
  }
  return result;
}
