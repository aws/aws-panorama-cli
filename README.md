# OmniDevPythonCLI

The purpose of this package is to provide a CLI tool to facilitate Panorama developer creating a local application as well as being able to upload the application to the cloud and deploy to device using the CLI.

## Dependencies

You will need Docker and AWS CLI installed on your machine.
Docker is required for building a package and AWS CLI is needed for downloading a model from S3 and packaging the application to Panorama Cloud.

## Setup

```
$ git clone https://github.com/aws/aws-panorama-cli
$ sudo ln -s <path_to_cloned_repo>/src/panorama-cli /usr/local/bin/panorama-cli
```

## Commands

Basic structure of the commands is as follows

```
$ panorama-cli <command> [options and parameters]
```

To view help documentation, use one of the following

```
$ panorama-cli -h
$ panorama-cli <command> -h
```

**Application development flow example**

This is an example of a sample app which has three node packages. people_counter package has core logic for counting the number of people, call_node has the model which people_counter package uses and rtsp_camera is the camera package.

```
$ panorama-cli init-project --name example_project
Successfully created the project skeleton at <path>

$ cd example_project

$ panorama-cli create-package --name people_counter

$ panorama-cli create-package --name call_node

$ panorama-cli create-package --name rtsp_camera -camera
```

Raw models are compiled using Sagemaker Neo on Panorama Cloud before being deployed onto the device. All models for this reason are paired with a descriptor json which has the required meta deta for compiling the raw model on the cloud.
Since call_node has the model in this example, edit `packages/accountXYZ-call-node-1.0/descriptor.json` and add the following snippet into it.
```
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

Now we can download the model by passing in the path to the descriptor file which we just updated.
```
$ panorama-cli download-raw-model --model-name callable_squeezenet --model-s3-uri s3://dx-cli-testing/raw_models/squeezenet1_0.tar.gz --descriptor-path packages/accountXYZ-call-node-1.0/descriptor.json
download: s3://dx-cli-testing/raw_models/squeezenet1_0.tar.gz to assets/callable_squeezenet.tar.gz
Successfully downloaded compiled artifacts (s3://dx-cli-testing/raw_models/squeezenet1_0.tar.gz) to ./assets/callable_squeezenet.tar.gz
Copy the following in the assets section of package.json
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
Paste the above json snippet into the assets section of call_node package to link the asset which we just downloaded to call_node package.

people_counter package has the core logic to count the number of people, so let's create a file called `people_counter_main.py` at `packages/accountXYZ-people-counter-package-1.0/src` and add the relevant code to that.
We can now build the package using the following command to create a container asset.
```
$ sudo panorama-cli build --package-name people_counter --package-path packages/619501627742-people-counter-package-1.0 --entry-file-path packages/accountXYZ-people-counter-package-1.0/src/people_counter_main.py
Add the following json snippet into the assets section of package.json at packages/619501627742-people-counter-package-1.0
{
    "name": "people_counter_container_binary",
    "implementations": [
        {
            "type": "container",
            "assetUri": "e8c30098e894b0f20555257bd4de023504690c63d889680f6ec125581a3dd2e7.tar.gz",
            "descriptorUri": "1c3a6a3ec9542bedcd3b5ec4fd083de9af0a1528f1496e0fb7fa2789c8155cfe.json"
        }
    ]
}
```
Copy the above json snippet into assets section of package.json at packages/619501627742-people-counter-package-1.0

Next step would be to edit all the package.json's and define interfaces for all the packages.
After that, you can edit the graph.json under `graphs` directory to define nodes from the above defined interfaces and add edges between them.
Refer to the example_app provided in this repository to better understand the changes that are needed.


When the applicaiton is ready, use the following command to upload all the packages to the cloud
```
$ panorama-cli package-application
```

After packaging the application, you can now use the graph.json from the package to start a deployment from the cloud!