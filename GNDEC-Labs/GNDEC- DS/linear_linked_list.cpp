#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
};

class LinearLinkedList {
private:
    Node* header;
    
public:
    LinearLinkedList() {
        header = new Node();
        header->next = nullptr;
    }
    
    ~LinearLinkedList() {
        Node* current = header->next;
        while (current != nullptr) {
            Node* temp = current;
            current = current->next;
            delete temp;
        }
        delete header;
    }
    
    void insertAtBeginning(int value) {
        Node* newNode = new Node();
        newNode->data = value;
        newNode->next = header->next;
        header->next = newNode;
    }
    
    void insertAtEnd(int value) {
        Node* newNode = new Node();
        newNode->data = value;
        newNode->next = nullptr;
        
        Node* current = header;
        while (current->next != nullptr) {
            current = current->next;
        }
        current->next = newNode;
    }
    
    void insertAtPosition(int value, int position) {
        if (position < 0) {
            cout << "Invalid position!" << endl;
            return;
        }
        
        Node* newNode = new Node();
        newNode->data = value;
        
        Node* current = header;
        for (int i = 0; i < position && current->next != nullptr; i++) {
            current = current->next;
        }
        
        newNode->next = current->next;
        current->next = newNode;
    }
    
    void deleteFromBeginning() {
        if (header->next == nullptr) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* temp = header->next;
        header->next = temp->next;
        delete temp;
    }
    
    void deleteFromEnd() {
        if (header->next == nullptr) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* current = header;
        while (current->next->next != nullptr) {
            current = current->next;
        }
        
        Node* temp = current->next;
        current->next = nullptr;
        delete temp;
    }
    
    void deleteFromPosition(int position) {
        if (header->next == nullptr) {
            cout << "List is empty!" << endl;
            return;
        }
        
        if (position < 0) {
            cout << "Invalid position!" << endl;
            return;
        }
        
        Node* current = header;
        for (int i = 0; i < position && current->next != nullptr; i++) {
            current = current->next;
        }
        
        if (current->next == nullptr) {
            cout << "Position out of range!" << endl;
            return;
        }
        
        Node* temp = current->next;
        current->next = temp->next;
        delete temp;
    }
    
    void display() {
        Node* current = header->next;
        if (current == nullptr) {
            cout << "List is empty!" << endl;
            return;
        }
        
        cout << "List: ";
        while (current != nullptr) {
            cout << current->data << " -> ";
            current = current->next;
        }
        cout << "NULL" << endl;
    }
};

int main() {
    LinearLinkedList list;
    
    cout << "=== Linear Linked List Operations ===" << endl;
    
    // Insertion operations
    cout << "\n--- Insertion Operations ---" << endl;
    list.insertAtEnd(10);
    list.insertAtEnd(20);
    list.insertAtEnd(30);
    list.display();
    
    list.insertAtBeginning(5);
    list.display();
    
    list.insertAtPosition(15, 2);
    list.display();
    
    // Deletion operations
    cout << "\n--- Deletion Operations ---" << endl;
    list.deleteFromBeginning();
    list.display();
    
    list.deleteFromEnd();
    list.display();
    
    list.deleteFromPosition(1);
    list.display();
    
    return 0;
}