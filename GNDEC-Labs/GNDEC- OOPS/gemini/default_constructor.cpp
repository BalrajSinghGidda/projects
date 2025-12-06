#include<iostream>
using namespace std;

class Student{
  public:
    string name;
    int roll_no;

    Student(){
      name = "Balraj Singh Gidda";
      roll_no = 2421212;
      cout << "Default constructor called" << endl;
    }

    void display(){
      cout << "Name: " << name << endl;
      cout << "URN: " << roll_no << endl;
      cout << "CRN: " << roll_no << endl;
    }
};

int main(){
  Student s;
  s.display();
  return 0;
}
