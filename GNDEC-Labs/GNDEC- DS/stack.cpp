#include<iostream>
#define MAX 15
using namespace std;

int stack[MAX];
int top = -1;

void push(int val) {
    if (top == MAX - 1) {
        cout << "Stack Overflow" << endl;
    } else {
        top++;
        stack[top] = val;
    }
}

int pop() {
    if (top == -1) {
        cout << "Stack Underflow" << endl;
        return -1;
    } else {
        int val = stack[top];
        top--;
        return val;
    }
}

int main() {
    push(10);
    push(20);
    cout << pop() << endl;
    cout << pop() << endl;
    cout << pop() << endl;
    return 0;
}
