#include<iostream>
using namespace std;
class A{
  public:
    int a;
    A(int a){
      this->a=a;
    }

    void display(){
      cout << "'this' value: " << this->a << endl;
    }
};

int main(){
  A O(10);
  int a = 5;
  cout << "'main' value: " << a << endl;
  O.display();
  return 0;
}

