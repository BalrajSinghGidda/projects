#include<iostream>
#include<fstream>
#include<string>
using namespace std;

int main(){
  fstream myfile("overloading.txt",ios::in|ios::out);

  if (!myfile.is_open()){
    cout << "Error" << endl;
    return 0;
  }
  myfile << "Hello ";
  myfile << "World" << endl;
  myfile.seekg(0);

  string line;

  while (getline(myfile,line)) {
    cout << line << endl;
    myfile.close();
  }

  return 0;
}
