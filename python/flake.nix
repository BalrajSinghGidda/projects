{
  description = "Dev shell: Python";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
        let
        pkgs = import nixpkgs { inherit system; };
        pythonEnv = pkgs.python313.withPackages (ps: with ps; [
          pytest
          black
          mypy
          isort
          flask
          sqlalchemy
          matplotlib
          memory-profiler
          flask-sqlalchemy
          flask-socketio
          numpy
          pandas
          eventlet
          werkzeug
          itsdangerous
          pip
          setuptools
          wheel
	  euporie
        ]);

        in {
        devShells.default = pkgs.mkShell {
        name = "python-devshell";
        buildInputs = [
        pythonEnv
        pkgs.poetry        
        pkgs.git
        pkgs.gdb          
        pkgs.ripgrep
        pkgs.nodejs      
        ];
        shellHook = ''
          export VIRTUAL_ENV_DISABLE_PROMPT=1
          clear
          echo "📦 Python devshell active — python ${pkgs.python313.version}"
          echo "Use: python, pip, pytest, black, mypy, poetry"
          '';
        };
    });
}

