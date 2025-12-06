#include<iostream>
#include<fstream>
#include<string>
using namespace std;

int main(){
  ofstream outfile("overloading.txt");
  if (outfile.is_open()) {
    outfile << "This is a text file." << endl;

    outfile.close();

    cout << "Text file saved!" << endl;
  }
  else {
    cout << "error" << endl;
  }
  return 0;
}
