#include <iostream>
#define MAX 10
using namespace std;

int queue[MAX];
int front = -1, rear = -1;

void enqueue(int x) {
    if (rear == MAX - 1) {
        cout << "Queue Overflow" << endl;
        return;
    }
    if (front == -1) {
        front = 0;
    }
    rear++;
    queue[rear] = x;
}

void dequeue() {
    if (front == -1 || front > rear) {
        cout << "Queue Underflow" << endl;
        return;
    }
    cout << "Element dequeued is: " << queue[front] << endl;
    front++;
}

void display() {
    if (front == -1) {
        cout << "Queue is empty" << endl;
        return;
    }
    cout << "Queue elements are: ";
    for (int i = front; i <= rear; i++) {
        cout << queue[i] << " ";
    }
    cout << endl;
}

int main() {
    int choice, val;
    cout << "1) Enqueue" << endl;
    cout << "2) Dequeue" << endl;
    cout << "3) Display" << endl;
    cout << "4) Exit" << endl;

    do {
        cout << "Enter your choice: ";
        cin >> choice;
        switch (choice) {
            case 1:
                cout << "Enter value to enqueue: ";
                cin >> val;
                enqueue(val);
                break;
            case 2:
                dequeue();
                break;
            case 3:
                display();
                break;
            case 4:
                cout << "Exit" << endl;
                break;
            default:
                cout << "Invalid choice" << endl;
        }
    } while (choice != 4);

    return 0;
}
