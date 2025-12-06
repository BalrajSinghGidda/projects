#include<iostream>
#include<string>

using namespace std;

class Example {
public:
    int id;
    string name;

    // Default Constructor
    Example() {
        id = 0;
        name = "Default";
        cout << "Default constructor called" << endl;
    }

    // Parameterized Constructor
    Example(int i, string n) {
        id = i;
        name = n;
        cout << "Parameterized constructor called" << endl;
    }

    // Copy Constructor
    Example(const Example &e) {
        id = e.id;
        name = e.name;
        cout << "Copy constructor called" << endl;
    }

    void display() {
        cout << "ID: " << id << ", Name: " << name << endl;
    }
};

int main() {
    cout << "Creating object with default constructor:" << endl;
    Example obj1;
    obj1.display();
    cout << endl;

    cout << "Creating object with parameterized constructor:" << endl;
    Example obj2(101, "Balraj");
    obj2.display();
    cout << endl;

    cout << "Creating object with copy constructor:" << endl;
    Example obj3 = obj2;
    obj3.display();
    cout << endl;

    return 0;
}
