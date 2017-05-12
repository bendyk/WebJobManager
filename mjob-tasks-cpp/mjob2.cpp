#include <fstream>
#include <iostream>
#include <stdint.h>
#include <unistd.h>
#include <array>
#include <string>
#include <stdlib.h>     /* srand, rand */
#include <time.h>

// bubble sort function
    void bubbleSort(int32_t array[], int32_t &arrAize) {
        int32_t c, d, swap;

        // sort the elements
        for (c = 0 ; c < ( arrAize - 1 ); c++) {
            for (d = 0 ; d < arrAize - c - 1; d++) {
                if (array[d] > array[d + 1]) { /* For decreasing order use < */
                    swap = array[d];
                    array[d] = array[d + 1];
                    array[d + 1] = swap;
                }
            }
        }
    }

    void arrayToString (int32_t array[], int32_t arraySize, std::string& arrayString) {
        for (int32_t i = 0; i < arraySize; ++i){
            arrayString += std::to_string(array[i]) + "\n"; // not so efficient
        }
     }


void outputResult(const std::string& data, const std::string& path) {
  std::fstream _handle;

  // open inwrite mode
  _handle.open(path, std::fstream::out | std::fstream::trunc);
  if (!_handle.is_open()) { // file does not exist
    std::cerr << "Failed to open result file (no permissions?)." << std::endl;
  }

  _handle << data << std::endl;
  _handle.close();
}

void readInput(const std::string& path, int32_t *arr, int32_t size) {
  std::fstream _handle;

  _handle.open(path, std::fstream::in);
  if (!_handle.is_open()) { // file does not exist
    std::cerr << "Failed to open input file (no permissions?)." << std::endl;
  }

    std::string line;

    for (int32_t i = 0; i < size && _handle.good(); ++i) {
      std::getline(_handle, line);
      arr[i] = std::stoi(line);
    }

  _handle.close();
}

int main(int argc, char **argv) {

		// declare the local unsorted1 array and it's size for the local functions
    int32_t arraySize = 500000/2;
    int32_t *unsorted1 = new int32_t[arraySize];

    // read from file
    std::string readpath(argv[1]);
    readInput(readpath, unsorted1, arraySize);

    // sort the unsorted1 array
    bubbleSort(unsorted1, arraySize);

    std::string outRes1;
    arrayToString(unsorted1, arraySize, outRes1);
    delete[] unsorted1;

    // write to result file
    std::string outpath(argv[1]);
    outpath += ".sort";

    outputResult(outRes1, outpath);
    return 0;
}

