# Greengrass Development Kit - Command Line Interface
![CI](https://github.com/aws-greengrass/aws-greengrass-gdk-cli/workflows/CI/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/aws-greengrass/aws-greengrass-gdk-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/aws-greengrass/aws-greengrass-gdk-cli)

### *Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.*
#### *SPDX-License-Identifier: Apache-2.0*

The AWS IoT Greengrass Development Kit Command-Line Interface (GDK CLI) provides features that help you develop custom Greengrass components. You can use the GDK CLI to create, build, and publish custom components. When you create a component repository with the GDK CLI, you can start from a template or a community component from the Greengrass Software Catalog.

Please follow the [GDK CLI public documentation](https://docs.aws.amazon.com/greengrass/v2/developerguide/greengrass-development-kit-cli.html) to learn more about the available commands and configuration that GDK CLI has to offer.

<br />

---

<br />

## Getting Started

#### Prerequisites
 1. [Python3](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/latest/installation/): As the GDK CLI tool is written in python, you need to have python3 and pip installed. The most recent version of python includes pip.

 2. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html): As you'd have to configure your AWS credentials using AWS CLI before running certain gdk commands.

#### 1. Installing CLI

To install the latest version of CLI using this git repository and pip, run the following command

`pip3 install git+https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git@v1.6.2`

Run `gdk --help` to check if the cli tool is successfully installed.

#### 2. Configure AWS credentials

Configure AWS CLI with your credentials as shown here - https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html.

#### 3. Quick start wih HelloWorld component written in python

*Note: Following steps are focused as a quick start guide. For more detailed steps, refer [our documentation](https://docs.aws.amazon.com/greengrass/v2/developerguide/create-components.html#create-component-gdk-cli).*

1. Initializes new project with a HelloWorld Greengrassv2 component.

`gdk component init --template HelloWorld --language python -n HelloWorld`

2. Change directory to `HelloWorld`.

`cd HelloWorld`

3. Update configuration in `gdk-config.json`
   1. Config file `gdk-config.json` would have placeholders:
   ```json
    {
        "component": {
            "com.example.PythonHelloWorld": {
                "author": "<PLACEHOLDER_AUTHOR>",
                "version": "NEXT_PATCH",
                "build": {
                    "build_system": "zip"
                },
                "publish": {
                    "bucket": "<PLACEHOLDER_BUCKET>",
                    "region": "<PLACEHOLDER_REGION>"
                }
            }
        },
        "gdk_version": "1.0.0"
    }
   ```
   2. Replace `<PLACEHOLDER_AUTHOR>` with your name, `<PLACEHOLDER_BUCKET>` with a prefix for an Amazon S3 bucket name and `<PLACEHOLDER_REGION>` with an AWS region. The specified bucket will be created in the specified region if it doesn't exist (name format: `{PLACEHOLDER_BUCKET}-{PLACEHOLDER_REGION}-{account_number}`).
   3. After replace these value the `gdk-config.json` file should look similar to:
   ```json
    {
        "component": {
            "com.example.PythonHelloWorld": {
                "author": "J. Doe",
                "version": "NEXT_PATCH",
                "build": {
                    "build_system": "zip"
                },
                "publish": {
                    "bucket": "my-s3-bucket",
                    "region": "us-east-1"
                }
            }
        },
        "gdk_version": "1.0.0"
    }
   ```

4. Build the artifacts and recipes of the component.

`gdk component build`

5. Creates new version of the component in your AWS account.

`gdk component publish`

#### 4. Deploy Component for local development

When developing components for AWS IoT Greengrass, you may want to deploy and test them locally. This command can deploy component using [greengrass-cli](https://docs.aws.amazon.com/greengrass/v2/developerguide/gg-cli-reference.html).

`gdk component local list|deploy|remove` command can deploy|remove|list yout component to your Greengrass Core running local (or running on remote device). The command sends command over SSH command when you specift remote device.

1. Update configuration in `gdk-config.json`
   ```json
    {
        "component": {
            "com.example.PythonHelloWorld": {
                "author": "J. Doe",
                "version": "NEXT_PATCH",
                "build": {
                    "build_system": "zip"
                },
                "publish": {
                    "bucket": "my-s3-bucket",
                    "region": "us-east-1"
                },
                "local":{
                    "host":"<host name or IP address>",
                    "port":"<Port number for ssh. default is 22>",
                    "user":"<User name used for SSH>",
                    "key_file":"<Identity file path used for SSH>",
                    "component_dir":"",
                    "greengrass_dir":""
                }
            }
        },
        "gdk_version": "1.0.0"
    }
   ```
    1. `local.host` is required when deploying to a remote device. In an environment where you connect to the outside through a proxy, please set the proxy in your ssh/config file.
    1. `local.port` is required when deploying to a remote device.
    1. `local.user` is required when deploying to a remote device.
    1. `local.key_file` is recommended when deploying to a remote device. Leave empty if password is used for authentication.
    1. `local.component_dir` is requiered when you want to specify the remote location. `~/greengrass-components` is used for default. This setting will be ignored when `local.host` is not specified(deploy component to the same device which is running Greengrass Core).
    1. `local.greengrass_dir` is requiered when you change Greengrass Core install directory. `/greengrass/v2` is used for default.


<br />

---


<br />

## Running Tests

<br />

* Unit tests: `make tests_unit`
* Integration tests: `make tests_integration`
