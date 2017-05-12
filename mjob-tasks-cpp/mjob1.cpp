#include <fstream>
#include <iostream>
#include <stdint.h>
#include <unistd.h>
#include <array>
#include <string>
#include <stdlib.h>     /* srand, rand */
#include <time.h>


// function to create arrays with random numbers
    void unsortedArrays (int32_t unsorted1[], int32_t unsorted2[], int32_t arrayElements) {
        for(int32_t i = 0; i < arrayElements; i++) { 
			unsorted1[i] = (arrayElements*2) - i;
            //unsorted1[i] = rand() % maxNum + minNum;
            unsorted2[i] = arrayElements - i;
            //unsorted2[i] = rand() % maxNum + minNum;
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

int main(int argc, char **argv) {
  if (argc < 2) {
    std::cerr << "please specify outpath." << std::endl;
    return 1;
  }
  // declare all the sizes
  const int32_t maxNum = 500000;
  const int32_t arrayElements = maxNum;

  // the arrays
  int32_t unsorted1[arrayElements/2];
  int32_t unsorted2[arrayElements/2];

  // fill the arrays with random numbers
  unsortedArrays(unsorted1, unsorted2, arrayElements/2);
  std::string outRes1, outRes2;

  arrayToString(unsorted1, arrayElements/2, outRes1);
  arrayToString(unsorted2, arrayElements/2, outRes2);

  // output arrays to file
  std::string p1(argv[1]);
  p1 += ".arr1";
  std::string p2(argv[1]);
  p2 += ".arr2";
  outputResult(outRes1, p1);
  outputResult(outRes2, p2);

  std::cout << "finished creating unsorted arrays" << std::endl;

  return 0;
}

