{
  description = "mplay kodi addon";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
    nixpkgs-unstable.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        mplayBuilder = kodi: kodi.packages.callPackage (
          { buildKodiAddon, urllib3, lib, ... }: buildKodiAddon {
            pname = "mplay";
            namespace = "plugin.program.mplay";
            version = "0.0.2";

            propagatedBuildInputs = [
              urllib3
            ];

            passthru = {
              pythonPath = with kodi.pythonPackages; makePythonPath [ levenshtein ];
            };

            src = ./.;
          }
        ) { };
      in rec {
        packages.mplay = mplayBuilder pkgs.kodi-wayland;
        packages.default = packages.mplay;
        
        apps.default = let
          kodi = pkgs.kodi-wayland.withPackages (kodiPkgs: [
            kodiPkgs.pvr-iptvsimple
            (mplayBuilder pkgs.kodi-wayland)
          ]);
        in {
          type = "app";
          program = toString (pkgs.writeShellScript "kodiEnv" ''
            export KODI_DATA=$(git rev-parse --show-toplevel)/.kodi
            exec ${kodi}/bin/kodi
          '');
        };

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            (python3.withPackages (ps: [ ps.urllib3 ]))
          ]; 
        };
      }
    );
}
