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
        lib = pkgs.lib;
        mplayVersion = lib.removeSuffix "\n" (builtins.readFile ./VERSION);
      in rec {
        packages.mplay = pkgs.stdenv.mkDerivation {
          name = "mplayBundle";
          version = mplayVersion;

          nativeBuildInputs = [ pkgs.zip ];

          # Only zip necessary content
          buildPhase = ''
            mkdir -p $out
            sed -e "s/@VERSION@/$(cat ./VERSION)/g" \
                addon.xml.in > addon.xml
            zip -r $out/mplay-${mplayVersion}.zip addon.xml src resources
          '';

          src = ./.;
        };
        packages.default = packages.mplay;
        
        # Provide kodi app with the addon installed for testing
        # Use $ nix run
        apps.default = let
          kodi = pkgs.kodi-wayland.withPackages (kodiPkgs: [
            kodiPkgs.pvr-iptvsimple
            (kodiPkgs.callPackage (
              { buildKodiAddon, urllib3, lib, unzip, ... }: buildKodiAddon {
                pname = "mplay";
                namespace = "context.program.mplay";
                version = mplayVersion;

                buildInputs = [
                  unzip
                ];

                propagatedBuildInputs = [
                  urllib3
                ];

                src = packages.mplay + "/mplay-${mplayVersion}.zip";
                sourceRoot = ".";
              }
            ) { })
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
