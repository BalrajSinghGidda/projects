#include<iostream>

using namespace std;

class MyClass {
  public:
    static int a;
};

int MyClass::a=125;

int main(){
  cout << "Static value: " << MyClass::a << endl;

  return 0;
}
