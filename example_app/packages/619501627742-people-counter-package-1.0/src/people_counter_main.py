import panoramasdk as p
import os
import time
import boto3
import logging
from logging.handlers import RotatingFileHandler
log = logging.getLogger('my_logger')
log.setLevel(logging.DEBUG)
handler = RotatingFileHandler("/panorama/logs/app.log", maxBytes=100000000, backupCount=2)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)
log.info("importing CV2")
try:
    import cv2
except Exception as e:
    log.error(e)
class people_counter(p.node):
    def __init__(self):
        try:
            self.message = 'Hello World',
            self.terminate = False
            with open('/panorama/storage/state.txt', 'a') as the_file:
                the_file.write('Successful Write on Startup\n')
                log.info("Write to Disk! !")
        except:
            pass
    def my_func(self):
            i = 0
            model_name = self.inputs.model_name.get()
            threshold = self.inputs.threshold.get()
            log.info(model_name)
            log.info('Connecting to AWS services..')
            s3 = boto3.client('s3')
            log.info('Connection to AWS services.. successful')
            log.info('Fetching S3 buckets')
            response = s3.list_buckets()
            log.info('Existing buckets:')
            for bucket in response['Buckets']:
                log.info(f' {bucket["Name"]}')
            while not self.terminate:
                self.terminate = False
                time.sleep(0.1)
                try:
                    #log.info(str(threshold))
                    if threshold < 60.1:
                        log.info("Demo3 with threshold less than 60.1")
                    outputFrames = []
                    frame = self.inputs.video_in.get()
                    for f in frame:
                        i = i + 1
                        log.info(str(f.image.shape))
                        log.info(str(i))
                        class_tuple = self.call({"data": f.image}, "classification_model")
                        log.info("Get results from class callable node")
                        log.info('**************')
                        for class_data in class_tuple:
                            log.info('Creating Shapes')
                            log.info(str(class_data.shape))
                            log.info('**************')
                            log.info(str(class_data.shape[0]))
                            log.info('Printing Class data whole')
                            log.info(str(class_data))
                        log.info('Demo 5 Model Inference Successful')
                except Exception as e:
                    log.error('Exception is {}'.format(e))
            return True
people_counter().my_func()