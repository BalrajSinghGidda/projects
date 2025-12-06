#include<iostream>
#include<fstream>
#include<string>
using namespace std;

int main(){
  ifstream inputfile("overloading.txt");

  string line;

  while (getline (inputfile,line)) {
    cout << line << endl;
    inputfile.close();
  }

  return 0;
}
