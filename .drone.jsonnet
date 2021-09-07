local name = "notes";
local browser = "firefox";

local build(arch, testUI) = {
    kind: "pipeline",
    name: arch,

    platform: {
        os: "linux",
        arch: arch
    },
    steps: [
        {
            name: "version",
            image: "debian:buster-slim",
            commands: [
                "echo $(date +%y%m%d)$DRONE_BUILD_NUMBER > version",
                "echo device.com > domain"
            ]
        },
        {
            name: "build-server",
            image: "golang:1.16.4",
            commands: [
                "./build-server.sh"
            ]
        },
        {
            name: "build-web",
            image: "node:14.17.5-alpine3.12",
            commands: [
                "./build-web.sh"
            ]
        },
        {
            name: "package",
            image: "debian:buster-slim",
            commands: [
                "VERSION=$(cat version)",
                "./package-python.sh",
                "./package.sh " + name + " $VERSION"
            ],
            volumes: [
            {
                name: "docker",
                path: "/usr/bin/docker"
            },
            {
                name: "docker.sock",
                path: "/var/run/docker.sock"
            }
            ]
        },
        {
            name: "test-integration",
            image: "python:3.8-slim-buster",
            commands: [
              "apt-get update && apt-get install -y sshpass openssh-client netcat rustc apache2-utils libffi-dev",
              "pip install -r dev_requirements.txt",
              "APP_ARCHIVE_PATH=$(realpath $(cat package.name))",
              "DOMAIN=$(cat domain)",
              "cd integration",
              "py.test -x -s verify.py --domain=$DOMAIN --app-archive-path=$APP_ARCHIVE_PATH --device-host=notes.device.com --app=" + name
            ]
        }
        ] + ( if testUI then [
        {
            name: "test-ui",
            image: "python:3.8-slim-buster",
            commands: [
              "apt-get update && apt-get install -y sshpass openssh-client libffi-dev",
              "pip install -r dev_requirements.txt",
              "DOMAIN=$(cat domain)",
              "cd integration",
              "py.test -x -s test-ui.py --ui-mode=mobile --domain=$DOMAIN --device-host=notes.device.com --app=" + name + " --browser=" + browser,
              "py.test -x -s test-ui.py --ui-mode=desktop --domain=$DOMAIN --device-host=notes.device.com --app=" + name + " --browser=" + browser
            ],
            volumes: [{
                name: "shm",
                path: "/dev/shm"
            }]
        }] else [] ) + [
        {
            name: "upload",
            image: "python:3.8-slim-buster",
            environment: {
                AWS_ACCESS_KEY_ID: {
                    from_secret: "AWS_ACCESS_KEY_ID"
                },
                AWS_SECRET_ACCESS_KEY: {
                    from_secret: "AWS_SECRET_ACCESS_KEY"
                }
            },
            commands: [
              "VERSION=$(cat version)",
              "PACKAGE=$(cat package.name)",
              "pip install syncloud-lib s3cmd",
              "syncloud-upload.sh " + name + " $DRONE_BRANCH $VERSION $PACKAGE"
            ]
        },
        {
            name: "artifact",
            image: "appleboy/drone-scp",
            settings: {
                host: {
                    from_secret: "artifact_host"
                },
                username: "artifact",
                key: {
                    from_secret: "artifact_key"
                },
                timeout: "2m",
                command_timeout: "2m",
                target: "/home/artifact/repo/" + name + "/${DRONE_BUILD_NUMBER}-" + arch,
                source: "artifact/*",
		             strip_components: 1
            },
            when: {
              status: [ "failure", "success" ]
            }
        }
    ],
    services: [{
        name: "notes.device.com",
        image: "syncloud/systemd-" + arch,
        privileged: true,
        volumes: [
            {
                name: "dbus",
                path: "/var/run/dbus"
            },
            {
                name: "dev",
                path: "/dev"
            }
        ]
    }],
    volumes: [
        {
            name: "dbus",
            host: {
                path: "/var/run/dbus"
            }
        },
        {
            name: "dev",
            host: {
                path: "/dev"
            }
        },
        {
            name: "shm",
            temp: {}
        },
        {
            name: "docker",
            host: {
                path: "/usr/bin/docker"
            }
        },
        {
            name: "docker.sock",
            host: {
                path: "/var/run/docker.sock"
            }
        }
    ]
};

[
    build("arm", false),
    build("amd64", true),
    build("arm64", false)
]
