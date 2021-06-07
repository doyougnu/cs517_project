with import <unstable> {};
let
  pythonEnv = python39.withPackages (ps: [
    ps.numpy
    ps.matplotlib
    ps.toolz
    ps.z3
    ps.importmagic
    ps.epc
    ps.python-igraph
    ps.networkx
    ps.jupyter
    ps.pycairo
    ps.pytest
    ps.pytest-benchmark
  ]);
in mkShell {
  buildInputs = [
    pythonEnv
    z3
    cairo
    qt4
    python3
    python3.pkgs.requests
  ];
  shellHook = ''
    # Tells pip to put packages into $PIP_PREFIX instead of the usual locations.
    # See https://pip.pypa.io/en/stable/user_guide/#environment-variables.
    export PIP_PREFIX=$(pwd)/_build/pip_packages
    export PYTHONPATH="$PIP_PREFIX/${pkgs.python3.sitePackages}:$PYTHONPATH"
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    export PATH="$PIP_PREFIX/bin:$PATH"
    unset SOURCE_DATE_EPOCH
  '';
}
