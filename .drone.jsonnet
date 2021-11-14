local name = "standardnotes";

local build(arch, testUI, platform_image) = {
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
                "./package.sh $VERSION"
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
              "APP_ARCHIVE_PATH=$(realpath $(cat package.name))",
              "cd integration",
              "pip install -r requirements.txt",
              "py.test -x -s verify.py --app-archive-path=$APP_ARCHIVE_PATH --app=" + name
            ]
        }
        ] + ( if testUI then [
        {
            name: "test-ui-desktop",
            image: "python:3.8-slim-buster",
            commands: [
              "apt-get update && apt-get install -y sshpass openssh-client libffi-dev",
              "cd integration",
              "pip install -r requirements.txt",
              "py.test -x -s test-ui.py --ui-mode=desktop --app=" + name
            ],
            volumes: [{
                name: "shm",
                path: "/dev/shm"
            }]
        },
        {
            name: "test-ui-mobile",
            image: "python:3.8-slim-buster",
            commands: [
              "apt-get update && apt-get install -y sshpass openssh-client libffi-dev",
              "cd integration",
              "pip install -r requirements.txt",
              "py.test -x -s test-ui.py --ui-mode=mobile --app=" + name
            ],
            volumes: [{
                name: "shm",
                path: "/dev/shm"
            }]
        }
        ] else [] ) + [
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
        name: app + ".device.com",
        image: "syncloud/" + platform_image,
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
    }] + ( if testUI then [{
            name: "selenium",
            image: "selenium/standalone-" + browser + ":4.0.0-beta-3-prerelease-20210402",
            volumes: [{
                name: "shm",
                path: "/dev/shm"
            }]
        }] else []),
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
    build("arm", false, "platform-buster-arm:21.10"),
    build("amd64", true, "platform-buster-amd64:21.10"),
    build("arm64", false, "platform-buster-arm64:21.10")
]
