{
  description = "Simple fullscreen clock app";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in rec {
        packages = rec {
          default = clockgr-gtk;

          clockgr-gtk = pkgs.python3Packages.buildPythonPackage {
            name = "clockgr-gtk";

            src = nixpkgs.lib.cleanSource ./.;

            nativeBuildInputs = with pkgs; [
              gobject-introspection
              wrapGAppsHook
              gtk3
            ];

            propagatedBuildInputs = with pkgs.python3Packages; [
              pycairo
              pygobject3
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
