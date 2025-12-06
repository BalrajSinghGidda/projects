#include<iostream>
using namespace std;

class veh{
	public:
	virtual void move()=0; // <-- pure virtual fn
};

class car:public veh{
  public:
  void move() override{
		cout << "Car" << endl;
	}
};

class boat:public veh{
  public:
  void move() override{
		cout << "Boat" << endl;
	}
};

int main(){
	car c;
	boat b;

	c.move();
	b.move();

	return 0;
}
