{
  description = "brobots air raid alerts bot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { nixpkgs, pyproject-nix, uv2nix, pyproject-build-systems, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
      overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };

      python = pkgs.python311;
      pythonBase =
        pkgs.callPackage pyproject-nix.build.packages { inherit python; };

      pythonSet = pythonBase.overrideScope (pkgs.lib.composeManyExtensions [
        pyproject-build-systems.overlays.wheel
        overlay
        (final: prev: {
          peewee = prev.peewee.overrideAttrs (old: {
            nativeBuildInputs = (old.nativeBuildInputs or [ ])
              ++ [ final.setuptools final.wheel ];
          });

          tornado = prev.tornado.overrideAttrs (old: {
            nativeBuildInputs = (old.nativeBuildInputs or [ ])
              ++ [ final.setuptools final.wheel ];
          });
        })
      ]);
    in {
      devShells.${system}.default = let
        editableOverlay =
          workspace.mkEditablePyprojectOverlay { root = "$REPO_ROOT"; };
        editablePythonSet = pythonSet.overrideScope editableOverlay;

        virtualenv = editablePythonSet.mkVirtualEnv "brobots-alerts-dev-env"
          workspace.deps.all;
      in pkgs.mkShell {
        packages = [ virtualenv pkgs.uv ];

        env = {
          UV_NO_SYNC = "1";
          UV_PYTHON = editablePythonSet.python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };

        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
        '';
      };

      packages.${system}.default =
        pythonSet.mkVirtualEnv "brobots-alerts-env" workspace.deps.default;

      nixosModules.brobots-alerts = { config, pkgs, lib, ... }:
        let cfg = config.services.brobots-alerts;
        in {
          options.services.brobots-alerts = {
            enable = lib.mkEnableOption "Enable brobots air raid alerts bot";
            environmentFile = lib.mkOption {
              type = lib.types.path;
              description = ".env file with secrets";
            };
          };

          config = lib.mkIf config.services.brobots-alerts.enable {
            users.users.brobots-alerts = {
              description = "brobots air raid alerts user";
              isSystemUser = true;
              group = "brobots-alerts";
            };

            systemd.services.brobots-air-raid-alerts = {
              description = "brobots air raid alerts service";
              after = [ "network.target" ];
              wants = [ "network-online.target" ];
              wantedBy = [ "multi-user.target" ];

              serviceConfig = {
                User = "brobots-alerts";
                Group = "brobots-alerts";

                ExecStart =
                  "${pkgs.${system}.brobots-alerts-env}/bin/python -m main";
                EnvironmentFile = cfg.environmentFile;

                Type = "simple";
                Restart = "on-failure";
              };
            };
          };
        };
    };
}
