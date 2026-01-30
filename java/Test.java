class Test {
  public static void main(String[] args) {
    int x = 3;
    int y = 4;
    int z = 3;
    if (x > y && y > z) {
      System.out.println("x > y && y > z is true");
    } else {
      System.out.println("x > y && y > z is false");
    }

    if (z == x && y > z) {
      System.out.println("z == x && y > z is true");
    } else {
      System.out.println("z == x && y > z is false");
    }

    if (x == y || x > z) {
      System.out.println("x == y || x > z is true");
    } else {
      System.out.println("x == y || x > z is false");
    }

  }
}
