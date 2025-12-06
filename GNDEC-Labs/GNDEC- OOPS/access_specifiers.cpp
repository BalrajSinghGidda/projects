#include<iostream>
using namespace std;

class RealLife{
  private:
    string name;
    int age;
  protected:
    string healthcare;
    void set_healthcare(string S_healthcare){
      healthcare=S_healthcare;
    }
  public:
    void set_det( const string S_name, int S_age, string S_healthcare ){
      name = S_name;
      age=S_age;
      healthcare=S_healthcare;
    }

    void display(){
      cout << "Name: " << name << endl;
      cout << "Age: " << age << endl;
      cout << "Health: " << healthcare << endl;
    }
};

int main(){
 RealLife S;
 S.set_det("Balraj", 20, "Good!");

 S.display();

 return 0;
}
