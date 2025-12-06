#include<iostream>
using namespace std;

class Employee{
  public:
    int id;
    string name;

    Employee(int i, string n){
      id = i;
      name = n;
      cout << "Parameterized constructor called" << endl;
    }

    void display(){
      cout << "ID: " << id << endl;
      cout << "Name: " << name << endl;
    }
};

int main(){
  Employee e(101, "Balraj");
  e.display();
  return 0;
}
