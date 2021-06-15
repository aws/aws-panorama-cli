# OmniDevPythonCLI

The purpose of this package is to provide a CLI tool to facilitate Panorama developer creating a local application as well as being able to upload the application to the cloud and deploy to device using the CLI.

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

```
$ panorama-cli init-project --name example_project
Successfully created the project skeleton at <path>

$ cd example_project

$panorama-cli create-package --name people_counter
Successfully created people_counter package

$ panorama-cli compile-model --model-s3-input-uri s3://<path>/resnet18_model.tar.gz --model-s3-output-uri s3://<path>/compiled_models/  --framework PYTORCH --input-shape 1 3 224 224 --compile-role-arn arn:aws:iam::12341234:role/Admin
Successfully created model compilation job with id: 8fc8b572

$ panorama-cli download-model --model-name resnet18
Compilation job completed. Downloading model artifacts...
Successfully downloaded compiled artifacts (s3://<path>/compiled_models/8fc8b572/resnet18_model-LINUX_ARM64_NVIDIA.tar.gz) to ./assets/b34a8c8eeb7c21cfb93f8715e6acfb4180add00d13b40e4d6488b8fd5e659be8/resnet18.tar.gz
Copy the following in the assets section of package.json of the package where the model is being used
{
    "name": "resnet18",
    "implementations": [
        {
            "type": "model",
            "assetUri": "b34a8c8eeb7c21cfb93f8715e6acfb4180add00d13b40e4d6488b8fd5e659be8",
        }
    ]
}

```

To use a precompiled Sagemaker Neo mode
```
$ panorama-cli download-model --model-name callable_squeezenet --model-s3-uri s3://<path>/compiled_models/ssd.tar.gz
Copy the following in the assets section of package.json of the package where the model is being used
{
    "name": "callable_squeezenet",
    "implementations": [
        {
            "type": "model",
            "assetUri": "3b39f4956d4d86c0b7de70486a67106e850b82c5e04a104b4828b6c8ac2965fb.sqfs"
        }
    ]
}
```

Add package specific code into src directory of the package and then use the following command to build a package.
Also add the package entry file path into the descript.json
```
$ sudo panorama-cli build --package-name people_counter --package-path packages/accountXYZ-people_counter-1.0 --entry-file-path packages/accountXYZ-people_counter-1.0/src/<package_entry_file_name>
```


When the applicaiton is ready, use the following command to upload all the packages to the cloud
```
$ panorama-cli package-application
```







