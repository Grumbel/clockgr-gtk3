{
  description = "Simple fullscreen clock app";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        packages = rec {
          default = clockgr-gtk;

          clockgr-gtk = pkgs.python3Packages.buildPythonPackage {
            name = "clockgr-gtk";
            src = nixpkgs.lib.cleanSource ./.;
            nativeBuildInputs = [
              pkgs.gobject-introspection
              pkgs.wrapGAppsHook
              pkgs.gtk3
            ];
            propagatedBuildInputs = [
              pkgs.python3Packages.pycairo
              pkgs.python3Packages.pygobject3
            ];
          };
        };

        apps = rec {
          default = clockgr-gtk3;

          clockgr-gtk3 = flake-utils.lib.mkApp {
            drv = packages.clockgr-gtk;
            exePath = "/bin/clockgr-gtk";
          };
        };
      }
    );
}
