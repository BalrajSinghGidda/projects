#include<iostream>
using namespace std;

class Fact{
  public:
    int calFact(int n){
      if (n<=1){
        return 1;
      }
        return n*calFact(n-1);
    }
};

int main(){
  Fact F;
  int n;

  cout << "Enter the number to calculate the factorial of: ";

  cin >> n;

  int r=F.calFact(n);

  cout << "The factorial of " << n << " is " << r << endl;

  return 0;
}
