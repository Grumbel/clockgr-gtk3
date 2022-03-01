{
  description = "Simple fullscreen clock app";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-21.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in rec {
        packages = flake-utils.lib.flattenTree rec {
          clockgr-gtk3 = pkgs.python3Packages.buildPythonPackage {
            name = "clockgr-gtk3";
            src = nixpkgs.lib.cleanSource ./.;
            nativeBuildInputs = [
              pkgs.gobject-introspection
              pkgs.gtk3
            ];
            propagatedBuildInputs = [
              pkgs.python3Packages.pycairo
              pkgs.python3Packages.pygobject3
            ];
          };
        };
        defaultPackage = packages.clockgr-gtk3;
      });
}
