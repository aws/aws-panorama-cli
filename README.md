# PanoramaDevPythonCLI

The purpose of this package is to provide a CLI tool to facilitate Panorama developer creating a local application as well as being able to upload the application to the cloud using the CLI.

## Dependencies

You will need Docker and AWS CLI installed on your machine.
Docker is required for building a package and AWS CLI is needed for downloading a model from S3 and packaging the application to Panorama Cloud.

##### Docker Setup

https://docs.docker.com/get-docker/

Since Panorama CLI builds ARM Docker images, it needs these extra steps on Linux to build cross platform images. Installing Docker Desktop on Mac should automatically handle cross platform builds.

On Debian based distros
```Shell
$ sudo apt-get install qemu binfmt-support qemu-user-static
$ sudo docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

On CentOS/RHEL based distros
```Shell
$ sudo yum install qemu binfmt-support qemu-user-static
$ sudo docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

##### AWS CLI Setup

https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html

AWS CLI version should be >=2.3.0 for v2 and >=1.21.0 for v1

## Install

Panorama CLI is only supported on Linux and macOS right now.

```Shell
$ pip3 install panoramacli
```

## Upgrade

To upgrade to the latest release

```Shell
$ pip3 install --upgrade panoramacli
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

### Related Github Repositories

Developer Guide - https://github.com/awsdocs/aws-panorama-developer-guide

Sample Applications - https://github.com/aws-samples/aws-panorama-samples

### Panorama Docs

https://docs.aws.amazon.com/panorama/

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

`rtsp_v1_interface` is the defined interface for an abstract camera and it has an output port called `video_out` which can be used to forward the camera output to another node. More details about connecting this camera are discussed in the [app graph section below](#defining-interfaces-and-app-graph)

#### Preparing a model for Panorama

Raw models are compiled using Sagemaker Neo on Panorama Cloud before being deployed onto the device. All models for this reason are paired with a `descriptor.json` which has the required meta deta for compiling the raw model on the cloud.

Details about using Sagemaker Neo to compile models can be found at https://docs.aws.amazon.com/sagemaker/latest/dg/neo-job-compilation.html

All the model info that is used to compile models on Sagemaker Neo are part of the `descriptor.json`. Values used in this example are specific to the squeezenet model that is being used in this example.

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
            }
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
FROM public.ecr.aws/panorama/panorama-application
COPY src /panorama
```

In the second line, we are basically copying all the contents of the `src` directory into the `/panorama` directory of the Docker image. Therefore, its important to note that when `people_counter_main.py` accesses other files which were originally part of the `src` directory, they are actually under `/panorama` when the application is running on the Panorama Appliance.

##### Handling dynamic data

Since all the containers run in read-only mode on the Panorama Appliance, its not possible to create new files at all paths. To facilitate this, Panorama base image(i.e first line in Dockerfile) has two directories `/opt/aws/panorama/logs` and `/opt/aws/panorama/storage` which are empty. During runtime, these directories are mounted to the device file system and allow the developer to store new files and data dynamically.

`/opt/aws/panorama/logs` is the location to store all the logs and all files created in the directory are uploaded to CloudWatch for the account which was used to provision the device.
`/opt/aws/panorama/storage` is a good location to store all the dynamic info that the application might need.
When the device re-starts, all the memory locations are deleted but the data under these two directories is persistent and therefore should contain all the context for the application to function from where it left off on a reboot.

##### Installing dependencies

The image(`public.ecr.aws/panorama/panorama-application`) provided by Panorama is a ARM64v8 Ubuntu image with just Panorama base software installed so all the additional dependencies for the application must be installed separately. For example, add the following line to the Dockerfile to install OpenCV and boto3. This Dockerfile fetches the latest `panorama-application` image by default, to use a specific version of the image, refer to https://gallery.ecr.aws/panorama/panorama-application and tag the image in the Dockerfile with the version you're planning to use.

```dockerfile
FROM public.ecr.aws/panorama/panorama-application
COPY src /panorama
RUN pip3 install opencv-python boto3
```

#### Overriding Abstract Cameras

We added an Abstract Camera in [setting up cameras section](#setting-up-cameras-for-panorama). If you're deploying an app through Panorama console, you will be automatically promted to replace the abstract camera node with a data source in your account. This section mentions how to create an `override.json` which can be used to replace abstract camera with a real camera while deploying applications from command line.

Create a Camera node using the following command. `--output-package-name` is the name of the camera package and `--node-name` specifies the node name under this package. We are keeping the names for both of these as `my_rtsp_camera` to keep it simple. Update `--template-parameters` with the correct Username, Password and StreamUrl.

```Shell
$ aws panorama create-node-from-template-job --template-type RTSP_CAMERA_STREAM --output-package-name my_rtsp_camera --output-package-version "1.0" --node-name my_rtsp_camera --template-parameters '{"Username":"admin","Password":"123456","StreamUrl": "rtsp://<url>"}'
```

This command will return an output like

```Shell
{
    "JobId": "d1d81752-d8ab-4131-8e48-8cf638685e71"
}
```

Let's make sure camera was created successfully by running the following command using the job id from above.

```Shell
$ aws panorama describe-node-from-template-job --job-id d1d81752-d8ab-4131-8e48-8cf638685e71
{
    "JobId": "d1d81752-d8ab-4131-8e48-8cf638685e71",
    "Status": "SUCCEEDED",
    "CreatedTime": "2021-10-11T13:22:51.284000-07:00",
    "LastUpdatedTime": "2021-10-11T13:22:51.284000-07:00",
    "OutputPackageName": "my_rtsp_camera",
    "OutputPackageVersion": "1.0",
    "NodeName": "my_rtsp_camera_node",
    "NodeDescription": "my_rtsp_camera_node",
    "TemplateType": "RTSP_CAMERA_STREAM",
    "TemplateParameters": {
        "Password": "SAVED_AS_SECRET",
        "StreamUrl": "rtsp://<url>",
        "Username": "SAVED_AS_SECRET"
    }
}
```

Since the status says succeeded, we are now ready to use this camera. Now, let's create an `override.json` for this camera. Here we are replacing `front_door_camera` node which we created in [setting up cameras section](#setting-up-cameras-for-panorama) with the newly created `my_rtsp_camera`

```JSON
{
  "nodeGraphOverrides" : {
    "envelopeVersion" : "2021-01-01",
    "packages" : [
        {
            "name" : "accountXYZ::my_rtsp_camera",
            "version" : "1.0"
        }
    ],
    "nodes" : [
        {
            "name" : "my_rtsp_camera_node",
            "interface" : "accountXYZ::my_rtsp_camera.my_rtsp_camera",
            "overridable" : true,
            "overrideMandatory" : false,
            "launch" : "onAppStart"
        }
    ],
    "nodeOverrides" : [
        {
            "replace" : "front_door_camera",
            "with" : [
                {
                    "name" : "my_rtsp_camera_node"
                }
            ]
        }
    ]
}
}
```

##### Processing streams from multiple cameras together

If you want to process streams from two or more cameras together, you can also replace the `front_door_camera` node with multiple cameras. For processing two streams together for example, create a second camera using the steps mentioned above and use the following override file.

```JSON
{
  "nodeGraphOverrides" : {
    "envelopeVersion" : "2021-01-01",
    "packages" : [
        {
            "name" : "accountXYZ::my_rtsp_camera",
            "version" : "1.0"
        },
        {
            "name" : "accountXYZ::my_other_camera",
            "version" : "1.0"
        }
    ],
    "nodes" : [
        {
            "name" : "my_rtsp_camera_node",
            "interface" : "accountXYZ::my_rtsp_camera.my_rtsp_camera",
            "overridable" : true,
            "overrideMandatory" : false,
            "launch" : "onAppStart"
        },
        {
            "name" : "my_other_camera_node",
            "interface" : "accountXYZ::my_other_camera.my_other_camera",
            "overridable" : true,
            "overrideMandatory" : false,
            "launch" : "onAppStart"
        }
    ],
    "nodeOverrides" : [
        {
            "replace" : "front_door_camera",
            "with" : [
                {
                    "name" : "my_rtsp_camera_node"
                },
                {
                    "name": "my_other_camera_node"
                }
            ]
        }
    ]
}
}
```

#### Using multiple cameras

At the end of last section, we looked at how to modify the override file we want to process streams from  multiple cameras together. This section speaks about using multiple camera streams in the same application and processing them separately. This is useful when multiple cameras are being used for different purposes.

Let's take the `package.json` of people_counter package from the [defining interfaces section](#defining-interfaces-and-app-graph) and modify it to have two video inputs.

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
                        "name": "video_in_1",
                        "type": "media"
                    },
                    {
                        "name": "video_in_2",
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

Let's add another camera to the application by using the following command.

```
$ panorama-cli add-panorama-package --type camera --name back_door_camera
```

A node named `back_door_camera` will be added into the `nodes` section of `graph.json` and let us connect both the cameras to the video inputs defined above in the `edges` section as shown below.

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
            },
            {
                "name": "back_door_camera",
                "interface": "panorama::abstract_rtsp_media_source.rtsp_v1_interface",
                "overridable": true,
                "launch": "onAppStart",
                "decorator": {
                    "title": "Camera back_door_camera",
                    "description": "Default description for camera back_door_camera"
                }
            }
        ],
        "edges": [
            {
                "producer": "front_door_camera_node.video_out",
                "consumer": "people_counter_container_binary_node.video_in_1"
            },
            {
                "producer": "back_door_camera_node.video_out",
                "consumer": "people_counter_container_binary_node.video_in_2"
            },
        ]
    }
}
```

#### Viewing output on a HDMI

In this people counter example application, if we also want to draw bounding boxes around people and view those processed frames on a screen, we can do that as well by adding a Data Sink node. Data Sink node forwards the input it receives to the HDMI port.

Like the abstract camera package, Panorama also provides a data sink package and we can create a data_sink using the following command.

```
$ panorama-cli add-panorama-package --type data_sink --name data_sink_node
```

This command adds the following node in the `nodes` section of `graph.json`

```
{
    "name": "data_sink_node",
    "interface": "panorama::hdmi_data_sink.hdmi0",
    "overridable": false,
    "launch": "onAppStart"
}
```

We can now connect this `data_sink_node` to the output of `people_counter_container_binary_node` in the `edges` section. At this point, `graph.json` looks as follows.

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
            {
                "name": "panorama::hdmi_data_sink",
                "version": "1.0"
            }
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
            },
            {
                "name": "data_sink_node",
                "interface": "panorama::hdmi_data_sink.hdmi0",
                "overridable": false,
                "launch": "onAppStart"
            }
        ],
        "edges": [
            {
                "producer": "front_door_camera_node.video_out",
                "consumer": "people_counter_container_binary_node.video_in"
            },
            {
                "producer": "people_counter_container_binary_node.video_out",
                "consumer": "data_sink_node.video_in"
            }
        ]
    }
}
```
