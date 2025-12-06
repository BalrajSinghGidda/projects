#include <iostream>
#include <algorithm> // for sort
using namespace std;

int main() {
    int n, k;
    cout << "Enter number of elements: ";
    cin >> n;

    int arr[n];
    cout << "Enter elements: ";
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    cout << "Enter k: ";
    cin >> k;

    // Sort the array in ascending order
    sort(arr, arr + n);

    if (k >= 1 && k <= n) {
        cout << "The " << k << "-th largest element is: " << arr[n - k] << endl;
    } else {
        cout << "Invalid value of k." << endl;
    }

    return 0;
}