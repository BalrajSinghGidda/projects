import java.util.*;

public class if_else_ladder {
  public static void main(String[] args) {
    int a, b, n, Result;

    Scanner sc = new Scanner(System.in);

    System.out.print("Enter a value for A: ");
    a = sc.nextInt();

    System.out.print("Enter a value for B: ");
    b = sc.nextInt();

    System.out.println("Select a number for an operation: ");
    System.out.print("1. Add; 2. Minus; 3. Multiply; 4. Divide : ");
    n = sc.nextInt();

    if (n == 1) {
      Result = a + b;
      System.out.print(Result);
    } else if (n == 2) {
      Result = a - b;
      System.out.print(Result);
    } else if (n == 3) {
      Result = a * b;
      System.out.print(Result);
    } else if (n == 4) {
      Result = a / b;
      System.out.print(Result);
    } else {
      System.out.print("--- Fatal Operation.. Try Again! ---");
    }

    sc.close();
  }
}
