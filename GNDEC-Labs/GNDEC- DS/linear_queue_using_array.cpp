#include <iostream>
#define MAX 10

using namespace std;

class LinearQueue {
private:
    int front;
    int rear;
    int arr[MAX];

public:
    LinearQueue() {
        front = -1;
        rear = -1;
    }

    void enqueue(int data) {
        if (rear == MAX - 1) {
            cout << "Queue Overflow\n";
            return;
        }
        if (front == -1) {
            front = 0;
        }
        rear++;
        arr[rear] = data;
    }

    void dequeue() {
        if (front == -1 || front > rear) {
            cout << "Queue Underflow\n";
            return;
        }
        cout << "Element deleted from queue is : " << arr[front] << "\n";
        front++;
    }

    void display() {
        if (front == -1) {
            cout << "Queue is empty\n";
            return;
        }
        cout << "Queue elements are : ";
        for (int i = front; i <= rear; i++) {
            cout << arr[i] << " ";
        }
        cout << "\n";
    }
};

int main() {
    LinearQueue q;
    q.enqueue(10);
    q.enqueue(20);
    q.enqueue(30);
    q.enqueue(40);
    q.display();
    q.dequeue();
    q.display();
    return 0;
}

