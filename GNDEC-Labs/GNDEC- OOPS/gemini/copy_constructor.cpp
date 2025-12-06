#include<iostream>
using namespace std;

class Car{
  public:
    string brand;
    string model;

    Car(string b, string m){
      brand = b;
      model = m;
    }

    Car(const Car &c){
      brand = c.brand;
      model = c.model;
      cout << "Copy constructor called" << endl;
    }

    void display(){
      cout << "Brand: " << brand << endl;
      cout << "Model: " << model << endl;
    }
};

int main(){
  Car c1("Audi", "A6");
  Car c2 = c1;

  cout << "Car 1:" << endl;
  c1.display();

  cout << "\nCar 2:" << endl;
  c2.display();

  return 0;
}

