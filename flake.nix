{
  description = "mplay kodi addon";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";

    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        mplayVersion = "0.1.0";
        mplayBuilder = kodiPackages: kodiPackages.callPackage (
          { buildKodiAddon, urllib3, lib, ... }: buildKodiAddon {
            pname = "mplay";
            namespace = "context.program.mplay";
            version = mplayVersion;

            propagatedBuildInputs = [
              urllib3
            ];

            src = ./.;
          }
        ) { };
      in rec {
        # Package mplay as a zip file for distribution
        packages.mplayBundle = pkgs.stdenv.mkDerivation {
          name = "mplayBundle";
          version = mplayVersion;

          nativeBuildInputs = [ pkgs.zip ];

          # Only zip necessary content
          buildPhase = ''
            mkdir -p $out
            zip -r $out/mplay-${mplayVersion}.zip addon.xml src resources
          '';

          src = ./.;
        };
        # Build the addon using the default buildKodiAddon function
        packages.mplay = mplayBuilder pkgs.kodi-wayland.packages;
        packages.default = packages.mplay;
        
        # Provide kodi app with the addon installed for testing
        # Use $ nix run
        apps.default = let
          kodi = pkgs.kodi-wayland.withPackages (kodiPkgs: [
            kodiPkgs.pvr-iptvsimple
            (mplayBuilder kodiPkgs)
          ]);
        in {
          type = "app";
          program = toString (pkgs.writeShellScript "kodiEnv" ''
            export KODI_DATA=$(git rev-parse --show-toplevel)/.kodi
            exec ${kodi}/bin/kodi
          '');
        };

        # Provide available python dependencies in shell
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            (python3.withPackages (ps: [ ps.urllib3 ]))
          ]; 
        };
      }
    );
}
