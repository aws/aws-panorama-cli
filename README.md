# PanoramaDevPythonCLI

The purpose of this package is to provide a CLI tool to facilitate Panorama developer creating a local application as well as being able to upload the application to the cloud and deploy to device using the CLI.

## Dependencies

You will need Docker and AWS CLI installed on your machine.
Docker is required for building a package and AWS CLI is needed for downloading a model from S3 and packaging the application to Panorama Cloud.

## Setup

```Shell
$ git clone https://github.com/aws/aws-panorama-cli
$ cd aws-panorama-cli
$ ./install.sh
Do not delete this directory. Created symlink to panorama-cli in /usr/local/bin. Run git pull for updates.
Successfully installed panorama-cli
```
(##### Internal)
Since Panorama service is not public yet, we have to setup the CLI for that as well. Follow the steps below for that to setup the CLI with PDX Gamma as endpoint.

Panorama currently supports PDX, IAD, DUB and YUL for regions.

```Shell
$ panorama-cli setup-panorama-service-cli --region PDX --stage Gamma
```

If you want to use the PDX Prod endpoint instead, you can use pass that as the stage

```Shell
$ panorama-cli setup-panorama-service-cli --region PDX --stage Prod
```

## Commands

Basic structure of the commands is as follows

```Shell
$ panorama-cli <command> [options and parameters]
```

To view help documentation, use one of the following

```Shell
$ panorama-cli -h
$ panorama-cli <command> -h
```

### Deploying a sample application

Instructions for downloading and deploying a sample application can be found at https://docs.aws.amazon.com/panorama/latest/dev/gettingstarted-deploy.html

### Application creation flow example

This is an example of a sample app which has two node packages. people_counter package has core logic for counting the number of people, call_node has the model which people_counter package uses. We will also add an abstract camera to the application which can be linked to a real camera from the console while deploying the application. 

```Shell
$ panorama-cli init-project --name example_project
Successfully created the project skeleton at <path>

$ cd example_project

$ panorama-cli create-package --name people_counter

$ panorama-cli create-package --name call_node --type Model
```

#### Application Structure

At this point, the application structure looks as follows.
`graph.json` under `graphs` directory lists down all the packages, nodes and edges in this application. Nodes and Edges are the way to define an application graph in Panorama.
`package.json` in each package has details about the package and the assets it uses. Interface definitions for the package need to be defined in this as well.
Model package `call-node` has a `descriptor.json` which needs to have the metadata required for compiling the model. More about this in the models section.
In `people_counter` package which is the default i.e container type, all the implementation related files go into the `src` directory and `descriptor.json` has details about which command and file to use when the container is launched. More about container package management later.
`assets` directory is where all the assets reside. Developer is not expected to make any changes in this directory.

```Shell
├── assets
├── graphs
│   └── example_project
│       └── graph.json
└── packages
    ├── accountXYZ-call_node-1.0
    │   ├── descriptor.json
    │   └── package.json
    └── accountXYZ-people_counter-1.0
        ├── Dockerfile
        ├── descriptor.json
        ├── package.json
        └── src
```

#### Setting up Cameras for Panorama

Panorama has a concept of Abstract Camera Package which the developers can use while developing their apps. This abstract camera package can be overriden and linked to an actual camera in the developer's Panorama account while deploying.

Let's add an abstract camera to this application by running the following command.

```
$ panorama-cli add-panorama-package --type camera --name front_door_camera
```

This command defines an abstract camera package in the `packages` section and adds the following snippet in the `nodes` section of the `graph.json`. You can modify the title and description to be more relevant to the use case.

```JSON
{
    "name": "front_door_camera",
    "interface": "panorama::abstract_rtsp_media_source.rtsp_v1_interface",
    "overridable": true,
    "launch": "onAppStart",
    "decorator": {
        "title": "Camera front_door_camera",
        "description": "Default description for camera front_door_camera"
    }
}
```

`rtsp_v1_interface` is the defined interface for an abstract camera and it has an output port called `video_out` which can be used to forward the camera output to another node. You can also find an example for this in the example_app's [graph.json](https://github.com/aws/aws-panorama-cli/blob/main/example_app/graphs/example_app/graph.json#L60) provided in this repository.

#### Preparing a model for Panorama

Raw models are compiled using Sagemaker Neo on Panorama Cloud before being deployed onto the device. All models for this reason are paired with a `descriptor.json` which has the required meta deta for compiling the raw model on the cloud.

Details about using Sagemaker Neo to compile models can be found at https://docs.aws.amazon.com/sagemaker/latest/dg/neo-job-compilation.html

All the model info that is used to compile models on Sagemaker Neo are part of the `descriptor.json`. Values used in this example are specific to the squeezenet model that is being used in this example.

If you want to use the same model as this example, you can use [this](https://amazon.awsapps.com/workdocs/index.html#/document/01f9aef8bbe885fa4b29fc6fa2bf23ae6f0c93973e201ef6f4da9d8b26378736) squeezenet model. 

Since call_node has the model in this example, edit `packages/accountXYZ-call-node-1.0/descriptor.json` and add the following snippet into it.
```JSON
{
    "mlModelDescriptor": {
        "envelopeVersion": "2021-01-01",
        "framework": "PYTORCH",
        "inputs": [
            {
                "name": "data",
                "shape": [
                    1,
                    3,
                    224,
                    224
                ]
            }
        ]
    }
}
```

Now we can add the model by passing in the path to the descriptor file which we just updated.

If you want to download the model from S3 and then add it pass `--model-s3-uri` as shown below. Otherwise just use `--model-local-path` to pass the local model path instead.

`--packages-path` can be used to pass all the packges where this model is being used and after downloading the model, DX CLI automatically adds the downloaded model into assets section of all the specified packages.

```Shell
$ panorama-cli add-raw-model --model-asset-name callable_squeezenet --model-s3-uri s3://<s3_bucket_path>/raw_models/squeezenet1_0.tar.gz --descriptor-path packages/accountXYZ-call_node-1.0/descriptor.json --packages-path packages/accountXYZ-call_node-1.0
download: s3://<s3_bucket_path>/squeezenet1_0.tar.gz to assets/callable_squeezenet.tar.gz
Successfully downloaded compiled artifacts (s3://<s3_bucket_path>/squeezenet1_0.tar.gz) to ./assets/callable_squeezenet.tar.gz
{
    "name": "callable_squeezenet",
    "implementations": [
        {
            "type": "model",
            "assetUri": "fd1aef48acc3350a5c2673adacffab06af54c3f14da6fe4a8be24cac687a386e.tar.gz",
            "descriptorUri": "df53d7bc3666089c2f93d23f5b4d168d2f36950de42bd48da5fdcafd9dbac41a.json"
        }
    ]
}
```

If you make any updates to your model or `desriptor.json` file after running this command, just re-run the command with the same `--model-asset-name` and the old asset will be updated with the new assets.

#### Writing code and building a container

people_counter package has the core logic to count the number of people, so let's create a file called `people_counter_main.py` at `packages/accountXYZ-people_counter-1.0/src` and add the relevant code to that.
Edit `packages/accountXYZ-people_counter-1.0/descriptor.json` to have the following content
```JSON
{
    "runtimeDescriptor":
    {
        "envelopeVersion": "2021-01-01",
        "entry":
        {
            "path": "python3",
            "name": "/panorama/people_counter_main.py"
        }
    }
}
```
descriptor.json basically provides the path for the command that needs to run and the path to the file that needs to be executed once the container starts.

(##### Internal) For building the container, you might need access to a private Dockerfile, reach out to prannoyp@ to get permissions. If you already have permissions and are still facing issues, run the following command to authenticate `aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 726743625486.dkr.ecr.us-west-2.amazonaws.com`
If you're using an older version of Dockerfile which has 500245141608 as account id in the image name, run the following command instead to authenticate `aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 500245141608.dkr.ecr.us-west-2.amazonaws.com`

We can now build the package using the following command to create a container asset.
```Shell
$ panorama-cli build-container --container-asset-name people_counter_container_binary --package-path packages/accountXYZ-people-counter-package-1.0
```

If you make any updates to your code or `desriptor.json` or `Dockerfile` file after building a container, just re-run the command with the same `--container-asset-name` and the old assets will be updated with the new assets.

#### Defining interfaces and app graph

Let's take a look at how the `package.json` looks for people_counter package after running build-container

```JSON
{
    "nodePackage": {
        "envelopeVersion": "2021-01-01",
        "name": "people_counter",
        "version": "1.0",
        "description": "Default description for package people_counter",
        "assets": [
            {
                "name": "people_counter_container_binary",
                "implementations": [
                    {
                        "type": "container",
                        "assetUri": "4e3a68e5fc0be9b7f3d8540a0a7d9855d6baae0b6dfc280b68431fd90b1e2c90.tar.gz",
                        "descriptorUri": "15545511b51d390a0a252537a41719498efd04f707deae17c6618d544e40e996.json"
                    }
                ]
            }
        ],
        "interfaces": [
            {
                "name": "people_counter_container_binary_interface",
                "category": "business_logic",
                "asset": "people_counter_container_binary",
                "inputs": [
                    {
                        "name": "video_in",
                        "type": "media"
                    }
                ],
                "outputs": [
                    {
                        "name": "video_out",
                        "type": "media"
                    }
                ]
            }
        ]
    }
}
```

A new asset named `people_counter_container_binary` has been added under assets and a new interface named `people_counter_container_binary_interface` has been defined. In Panorama, interfaces are a way to programtically interact with a package and each interface is linked to an asset. For example, `people_counter_container_binary_interface` has an asset field which points to `people_counter_container_binary`. That means that we are defining an interface to that asset. In this case, since our asset is a container with your code in it, all the inputs your code expects can be part of the inputs under interfaces. In this example, the code just expects one input which is a video stream. If output of your code needs to be consumed by another asset, that can be part of the ouputs. Similarly, a new interface was added to the call-node package when we can `add-raw-model` command. In that case, interface was linked to the model asset which we added using that command.

At this point, `graph.json` under the graphs directory looks like this

```JSON
{
    "nodeGraph": {
        "envelopeVersion": "2021-01-01",
        "packages": [
            {
                "name": "accountXYZ::people_counter",
                "version": "1.0"
            },
            {
                "name": "accountXYZ::call_node",
                "version": "1.0"
            },
            {
                "name": "panorama::abstract_rtsp_media_source",
                "version": "1.0"
            },
        ],
        "nodes": [
            {
                "name": "front_door_camera",
                "interface": "panorama::abstract_rtsp_media_source.rtsp_v1_interface",
                "overridable": true,
                "launch": "onAppStart",
                "decorator": {
                    "title": "Camera front_door_camera",
                    "description": "Default description for camera front_door_camera"
                }
            },
            {
                "name": "callable_squeezenet",
                "interface": "accountXYZ::call_node.callable_squeezenet_interface"
            },
            {
                "name": "people_counter_container_binary_node",
                "interface": "accountXYZ::people_counter.people_counter_container_binary_interface",
                "overridable": false,
                "launch": "onAppStart"
            }
        ],
        "edges": []
    }
}
```

`packages` section here has all the packages that are part of this application and we can see that `nodes` section has some nodes defined already. To be able to use any package, we need to define a corresponding nodes in the `graph.json` for all the interfaces that are part of the package. `people_counter_container_binary_node` node is linked to `people_counter_container_binary_interface` interface from people_counter package which we just looked at and similarly `callable_squeezenet` node is linked to `callable_squeezenet_interface` interface from the call_node package. We already discussed the `front_door_camera` node in [setting up cameras section](#setting-up-cameras-for-panorama)


Next thing we will do is set up the edges for the application graph. `people_counter_container_binary_interface` had one input `video_in` as part of the interface definition and that was the video input to the code in that package. We can connect that input to the camera node's output by adding the following edge under the `edges` section.

```JSON
"edges": [
            {
                "producer": "front_door_camera_node.video_out",
                "consumer": "people_counter_container_binary_node.video_in"
            },
        ]
    }
```

#### Registering and Uploading all local packages in the Cloud

When the application is ready, use the following command to upload all the packages to the cloud
```Shell
$ panorama-cli package-application
```

#### Deploying the application

After packaging the application, you can now use the graph.json from the package to start a deployment from the cloud!


### Panorama Application Concepts

#### Container Package Basics

##### Handling implementation related files

This is a directory tree of how an example container package. All the implementation related files for this package go into the `src` directory. In this package, `people_counter_main.py` has the logic for processing the frames from the camera and `people_counter_main.py` depends on `blueprint.csv` and `requirements.json` for some of its functionality and therefore those are under the `src` directory as well. If the application requires multiple `.py` files then all those will be under the `src` directory as well.

```Shell
accountXYZ-people_counter-1.0
├── Dockerfile
├── descriptor.json
├── package.json
└── src
    ├── blueprint.csv
    ├── people_counter_main.py
    └── requirements.json
```

Let's now take a look at the Dockerfile provided as part of the package

```dockerfile
FROM 726743625486.dkr.ecr.us-west-2.amazonaws.com/panorama-application
COPY src /panorama
```

In the second line, we are basically copying all the contents of the `src` directory into the `/panorama` directory of the Docker image. Therefore, its important to note that when `people_counter_main.py` accesses other files which were originally part of the `src` directory, they are actually under `/panorama` when the application is running on the Panorama Appliance.

##### Handling dynamic data

Since all the containers run in read-only mode on the Panorama Appliance, its not possible to create new files at all paths. To facilitate this, Panorama base image(i.e first line in Dockerfile) has two directories `/opt/aws/panorama/logs` and `/opt/aws/panorama/storage` which are empty. During runtime, these directories are mounted to the device file system and allow the developer to store new files and data dynamically.

`/opt/aws/panorama/logs` is the location to store all the logs and all files created in the directory are uploaded to CloudWatch for the account which was used to provision the device.
`/opt/aws/panorama/storage` is a good location to store all the dynamic info that the application might need.
When the device re-starts, all the memory locations are deleted but the data under these two directories is persistent and therefore should contain all the context for the application to function from where it left off on a reboot.

##### Installing dependencies

The image(`726743625486.dkr.ecr.us-west-2.amazonaws.com/panorama-application`) provided by Panorama is a ARMv8 Ubuntu image with just Panorama base software installed so all the additional dependencies for the application must be installed separately. For example, add the following line to the Dockerfile to install OpenCV and boto3.

```dockerfile
FROM 726743625486.dkr.ecr.us-west-2.amazonaws.com/panorama-application
COPY src /panorama
RUN pip3 install opencv-python boto3
```

