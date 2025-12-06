#include<iostream>
using namespace std;
class G{
  private:
    int pri;
  protected:
    int prot;
  public:
    G(){
      pri=10;
      prot=99;
    }
  friend class GG;
};

class GG{
  public:
    void display(G&t){
      cout << "Private Fn called: ";
      cout << t.pri << endl;
      cout << "Protected Fn called: ";
      cout << t.prot << endl;
    }
};

int main(){
  G g;
  GG f;

  f.display(g);
  return 0;
} 
