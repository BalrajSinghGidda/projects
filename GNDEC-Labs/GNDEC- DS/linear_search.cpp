#include <iostream>
using namespace std;

int main(){
    int n, x, b;
    
    cout << "Number of elements in the array: ";
    cin >> n;
    
    int a[n];
    
    for (int i = 0; i < n; i++){
        cout << "Enter element " << i + 1 << ": ";
        cin >> a[i];
    }
    
    cout << "Enter the element to search: ";
    cin >> x;
    
    b = -1;
    for (int i = 0; i < n; i++){
        if (a[i] == x) {
            b = i;
            break;  // Stop after first match (optional)
        }
    }

    if (b == -1)
        cout << "Element is not present!!";
    else
        cout << "The location of " << x << " is at index " << b << " (position " << b + 1 << ")";
}
