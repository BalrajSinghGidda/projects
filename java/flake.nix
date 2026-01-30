{
  description = "Dev shell: Java (JDK 21, Maven, Gradle)";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells.default = pkgs.mkShell {
          name = "java-devshell";

          packages = with pkgs; [
            jdk21
            maven
            gradle
            jdt-language-server
          ];

          shellHook = ''
            export JAVA_HOME=${pkgs.jdk21}
            echo "☕ Java devshell ready — JDK 21, Maven, Gradle"
          '';
        };
      });
}
