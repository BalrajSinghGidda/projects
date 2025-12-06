{
  description = "Dev shells: cpp";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:

    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
    devShells.default = pkgs.mkShell {
      name = "cpp-devshell";
      buildInputs = [
        pkgs.gcc
          pkgs.clang
          pkgs.cmake
          pkgs.ninja
          pkgs.gdb
          pkgs.ccache
          pkgs.pkg-config
          pkgs.boost
          pkgs.libsigcxx
      ];
      nativeBuildInputs = [ pkgs.stdenv.cc ];
      shellHook = ''
        export CC=gcc
        export CXX=g++
	clear
        echo "🔧 C++ devshell ready — gcc/clang, cmake, ninja, gdb, ccache"
        echo "If you use clang-tidy or clang-format add them to buildInputs"
        '';
      };
    });
}
