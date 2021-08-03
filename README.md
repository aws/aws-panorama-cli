# PanoramaDevPythonCLI

The purpose of this package is to provide a CLI tool to facilitate Panorama developer creating a local application as well as being able to upload the application to the cloud and deploy to device using the CLI.

## Dependencies

You will need Docker and AWS CLI installed on your machine.
Docker is required for building a package and AWS CLI is needed for downloading a model from S3 and packaging the application to Panorama Cloud.

After downloading both of these, since panorama service is not public yet, we have to setup the CLI for that as well. Follow the steps below for that to setup the CLI with Gamma as endpoint.

1. Download the [model/normal.json](https://amazon.awsapps.com/workdocs/index.html#/document/820db0cf75d55a1e604697d194ca929001dd7fcd27040abaf80836cd016898b1) file from artifacts under OmniCloudServiceLambdaModel as OmniCloudServiceLambda.api.json file.

2. Run the following command use IAD gamma endpoint:
```Shell
sed -i.bak  's-requestUri":"/-requestUri":"/gamma/-g; s/endpointPrefix":"panorama/endpointPrefix":"avvngkyyje.execute-api/g'  OmniCloudServiceLambda.api.json
```
or this one for PDX Gamma instead:
```Shell
sed -i.bak 's-requestUri":"/-requestUri":"/gamma/-g; s/endpointPrefix":"panorama/endpointPrefix":"6m0zzkt7pf.execute-api/g' OmniCloudServiceLambda.api.json
```


3.  Configure cli setup locally:
```Shell
aws configure add-model --service-model file://OmniCloudServiceLambda.api.json --service-name panorama
```

Since our PanoramaSDK image is not public yet, you might also face permission issues when you're trying the build command listed below. Reachout to prannoyp@ for getting access to the image.

## Setup

```Shell
$ git clone https://github.com/aws/aws-panorama-cli
$ sudo ln -s <absolute_path_to_cloned_repo>/src/panorama-cli /usr/local/bin/panorama-cli
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

**Deploying a sample application with assets downloaded**

Link to Samples Repo - to be added

Link to example application - https://amazon.awsapps.com/workdocs/index.html#/document/2a82b1fb07a92a33c3eb6654e3e747a22440d051d4aa4d3b652859e04290f204

Link to an application with HDMI Output - https://drive.corp.amazon.com/personal/ahahajar/GM2%20Template%20Model

```Shell
$ cd <application_directory>
$ panorama-cli import-application
$ panorama-cli package-application
```

**Application creation flow example**

This is an example of a sample app which has three node packages. people_counter package has core logic for counting the number of people, call_node has the model which people_counter package uses and rtsp_camera is the camera package.

```Shell
$ panorama-cli init-project --name example_project
Successfully created the project skeleton at <path>

$ cd example_project

$ panorama-cli create-package --name people_counter

$ panorama-cli create-package --name call_node -model

$ panorama-cli create-package --name rtsp_camera -camera
```

To setup the camera, modify the following snippet of the interfaces section of the package.json for rtsp_camera package and make sure asset points to the right path.
Update the username, password and streamUrl to the right values for your camera.
```JSON
{
                "description" : "Default desc",
                "name": "rtsp_interface",
                "category": "media_source",
                "asset": "rtsp_camera",
                "inputs":
                [
                    {
                        "description": "Camera username",
                        "name": "username",
                        "type": "string",
                        "default": "root"
                    },
                    {   
                        "description": "Camera password",
                        "name": "password",
                        "type": "string",
                        "default": "Aws2017!"
                    },
                    {
                        "description": "Camera streamUrl",
                        "name": "streamUrl",
                        "type": "string",
                        "default": "rtsp://10.92.200.68/onvif-media/media.amp?profile=profile_4_h264&sessiontimeout=60&streamtype=unicast"
                    }       
                ],
                "outputs":
                [
                    {
                        "description": "Video stream output",
                        "name": "video",
                        "type": "media"
                    }
                ]
}
```

Raw models are compiled using Sagemaker Neo on Panorama Cloud before being deployed onto the device. All models for this reason are paired with a descriptor json which has the required meta deta for compiling the raw model on the cloud.
If you want to use the same model as this example, you can use [this](https://amazon.awsapps.com/workdocs/index.html#/document/01f9aef8bbe885fa4b29fc6fa2bf23ae6f0c93973e201ef6f4da9d8b26378736) squeezenet model and upload it to your s3.

Since call_node has the model in this example, edit `packages/accountXYZ-call-node-1.0/descriptor.json` and add the following snippet into it. These values are specific to the squeezenet model that is being used in this example.
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
```Shell
$ panorama-cli add-raw-model --model-asset-name callable_squeezenet --model-s3-uri s3://<s3_bucket_path>/squeezenet1_0.tar.gz --descriptor-path packages/accountXYZ-call-node-1.0/descriptor.json
download: s3://<s3_bucket_path>/squeezenet1_0.tar.gz to assets/callable_squeezenet.tar.gz
Successfully downloaded compiled artifacts (s3://<s3_bucket_path>squeezenet1_0.tar.gz) to ./assets/callable_squeezenet.tar.gz
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
Paste the above json snippet into the assets section of call_node package.json to link the asset which we just downloaded to call_node package.

If call-node packages is specified as part of the command, asset snippet is copied into package.json automatically
```Shell
$ panorama-cli add-raw-model --model-asset-name callable_squeezenet --model-s3-uri s3://dx-cli-testing/raw_models/squeezenet1_0.tar.gz --descriptor-path packages/accountXYZ-call_node-1.0/descriptor.json --packages-path packages/accountXYZ-call_node-1.0
download: s3://dx-cli-testing/raw_models/squeezenet1_0.tar.gz to assets/callable_squeezenet.tar.gz
Successfully downloaded compiled artifacts (s3://dx-cli-testing/raw_models/squeezenet1_0.tar.gz) to ./assets/c399edb69582ff4c10dfdc4af86da49fccce442b9cda17351be8836ae3bd2417.tar.gz
```

people_counter package has the core logic to count the number of people, so let's create a file called `people_counter_main.py` at `packages/accountXYZ-people-counter-package-1.0/src` and add the relevant code to that.
Edit `packages/accountXYZ-people-counter-package-1.0/descriptor.json` to have the following content
```JSON
{
    "runtimeDescriptor":
    {
        "envelopeVersion": "2021-01-01",
        "entry":
        {
            "path": "python3",
            "name": "/Panorama/people_counter_main.py"
        }
    }
}
```
descriptor.json basically provides the path for the command that needs to run and the path to the file that needs to be executed once the container starts.

(Temporary) For building the container, you might need access to a private Dockerfile, reach out to prannoyp@ to get permissions. If you already have permissions and are still facing issues, run the following command to authenticate `aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 500245141608.dkr.ecr.us-west-2.amazonaws.com`
(Temporary until 8/2) If you're using the beta build for 4.1.11, modify the Dockerfile in the package directory and change `demo` in the first line to `experiment`

We can now build the package using the following command to create a container asset.
```Shell
$ panorama-cli build --container-asset-name people_counter_container_binary --package-path packages/accountXYZ-people-counter-package-1.0
```

Next step would be to edit all the package.json's and define interfaces for all the packages.
After that, you can edit the graph.json under `graphs` directory to define nodes from the above defined interfaces and add edges between them.
Refer to the example_app provided in this repository to better understand the changes that are needed.
example_app provided in this repository doesn't have the downloaded/built assets in it. You can find the entire application with all the assets at https://amazon.awsapps.com/workdocs/index.html#/document/2a82b1fb07a92a33c3eb6654e3e747a22440d051d4aa4d3b652859e04290f204

When the applicaiton is ready, use the following command to upload all the packages to the cloud
```Shell
$ panorama-cli package-application
```

After packaging the application, you can now use the graph.json from the package to start a deployment from the cloud!
