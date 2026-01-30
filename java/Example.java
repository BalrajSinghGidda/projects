import java.util.Scanner;

public class Example {
  private static Scanner sc;

  public static void main(String[] args) {
    int Num;
    sc = new Scanner(System.in);
    System.out.println("Please enter any int value: ");
    Num = sc.nextInt();
    System.out.println((Num >= 0) ? "\nPositive" : "\n Negative");
    sc.close();
  }
}
