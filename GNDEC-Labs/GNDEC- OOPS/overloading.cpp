#include<iostream>
using namespace std;

class Area{
  public:
    int Value(int a){
      int r=a*a;

      cout << "The area of square is: " << r << endl;

      return 0;
    };

    int Value(int l, int b){
      int i=l*b;

      cout << "The area of rectangle is: " << i << endl;

      return 0;
    }
};

int main(){
  int n;
  Area A;

  cout << "Enter 1 to calculate the area of SQUARE, or 2 for RECTANGLE: ";
  cin >> n;

  if (n==1){
    int a;
    cout << "Enter the value of the side: ";
    cin >> a;

    A.Value(a);
  }
  else if (n==2) {
    int l;
    int b;

    cout << "Enter the values for length and breadth: ";

    cin >> l >> b;

    A.Value(l, b);
  }
  else{
    cout << "Wrong Choice!!!!!!";
    return 0;
  }

  return 0;
}
