// #include<iostream>
// using namespace std;
// class comp{
//   int real, imag;
//   public:
//     comp(int r=0, int i=0):real(r),imag(i){
//
//     }
//     comp operator+(const comp&c){
//       return comp(real+c.real,imag+c.imag);
//     }
//
//   void display(){
//     cout << real << "+" << imag << "i\n";
//   }
// };
//
// int main(){
//   comp c1(3,3),c2(2,3),c3;
//   c3=c1+c2;
//   c3.display();
//   return 0;
// }


#include<iostream>
using namespace std;
class comp{
  int real, imag;
  public:
    comp(int r=0, int i=0):real(r),imag(i){

    }
    comp operator+(const comp&c){
      return comp(real+c.real,imag+c.imag);
    }

  void display(){
    cout << real << "+" << imag << "i\n";
  }
};

int main(){
  comp c1(3,3),c2(2,3),c3;
  c3=c1+c2;
  c3.display();
  return 0;
}
