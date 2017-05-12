#include <fstream>
#include <iostream>
#include <stdint.h>
#include <unistd.h>
#include <array>
#include <string>
#include <stdlib.h>     /* srand, rand */
#include <time.h>

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

// merge sort function
    void mergeSort(int32_t *arrayA, int32_t arrayASize, int32_t *arrayB, int32_t arrayBSize, int32_t *arrayC, int32_t arrayCSize) {
		int indexA = 0;     // initialize variables for the subscripts
		int indexB = 0;
		int indexC = 0;

		while((indexA < arrayASize) && (indexB < arrayBSize)) {
			if (arrayA[indexA] < arrayB[indexB]) {
				arrayC[indexC] = arrayA[indexA];
				indexA++;    //increase the subscript
			}
			else {
				arrayC[indexC] = arrayB[indexB];
				indexB++;      //increase the subscript
			}
			indexC++;      //move to the next position in the new array
		}
		
		// Move remaining elements to end of new array when one merging array is empty
		while (indexA < arrayASize) {
			arrayC[indexC] = arrayA[indexA];
			indexA++;
			indexC++;
		}
		while (indexB < arrayBSize) {
			arrayC[indexC] = arrayB[indexB];
			indexB++;
			indexC++;
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

    void arrayToString (int32_t array[], int32_t arraySize, std::string& arrayString) {
        for (int32_t i = 0; i < arraySize; ++i){
            arrayString += std::to_string(array[i]) + "\n"; // not so efficient
        }
     }


int main(int argc, char **argv) {

  if (argc < 3) {
    std::cerr << "Please specify two input files" << std::endl;
    return 1;
  }

  // declare the local unsorted1 array and it's size for the local functions
  const int32_t arraySize = 500000/2;
  int32_t *sorted1 = new int32_t[arraySize];
  int32_t *sorted2 = new int32_t[arraySize];
  int32_t *merged = new int32_t[arraySize*2];

  // read from file
  std::string inp1(argv[1]);
  std::string inp2(argv[2]);
  readInput(inp1, sorted1, arraySize);
  readInput(inp2, sorted2, arraySize);

  // merge sort
  mergeSort(sorted1, arraySize, sorted2, arraySize, merged, arraySize*2);
  
  // convert result to string object
  std::string outRes1;
  arrayToString(merged, arraySize*2, outRes1);
  delete[] sorted1;
  delete[] sorted2;
  delete[] merged;

  // write result
  std::string outpath(inp1);
  size_t lim = outpath.find_last_of('.');
  if (lim != std::string::npos && outpath.size() >= (lim + 4)) { // assume outpath is: *.srt+
    outpath[lim+1] = 'm';
    outpath[lim+2] = 'r';
    outpath[lim+3] = 'g';
    outpath[lim+4] = 'e';
  }

  outputResult(outRes1, outpath);

  std::cout << "Merged sorted content" << std::endl;
  return 0;
}

