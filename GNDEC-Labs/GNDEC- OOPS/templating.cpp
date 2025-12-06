#include<iostream>
using namespace std;

template<typename T>
class geek{
 public:
   T x;
   T y;

   geek(T val1, T val2):x(val1),y(val2){}

   void getval(){
     cout << x << " " << y;
   }
};

int main(){
  geek <int> intgeek(10,20);
  geek <double> doublegeek(10.5,20.5);

  intgeek.getval();
  cout << endl;
  doublegeek.getval();

  return 0;
}
