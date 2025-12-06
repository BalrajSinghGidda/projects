#include <iostream>
using namespace std;

int main(){
    int n, x;
    
    cout << "Number of elements in the array: ";
    cin >> n;
    
    int a[n];
    
    cout << "Enter the elements of the array in sorted order: " << endl;
    for (int i = 0; i < n; i++){
        cout << "Enter element " << i + 1 << ": ";
        cin >> a[i];
    }
    
    cout << "Enter the element to search: ";
    cin >> x;
    
    int low = 0, high = n - 1, mid;
    int b = -1;
    
    while(low <= high){
        mid = low + (high - low) / 2;
        if(a[mid] == x){
            b = mid;
            break;
        }
        else if(a[mid] < x){
            low = mid + 1;
        }
        else{
            high = mid - 1;
        }
    }

    if (b == -1)
        cout << "Element is not present!!";
    else
        cout << "The location of " << x << " is at index " << b << " (position " << b + 1 << ")";
}
