#include<iostream>
using namespace std;

class Person{
	public:
	Person(){
		cout << "Person construct." << endl;
	}

	virtual ~ Person(){
		cout << "Person Destruct." << endl;
	}
};

class Student:public Person{
	public:
	Student(){
		cout << "Student construct." << endl;
	}

	~ Student() override{
		cout << "Student destruct." << endl;
	}
};

int main(){
	Person *P = new Student();
	delete P;

	return 0;
}
