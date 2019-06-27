# The Multisensor Labeler

The labeler sysem currently takes any two sensors, and creates a bounding box on all images at the same time based on isolated blobs within sensor two. This allows you to quickly label based on a specific item. It is extremely helpful when you can threshold out an object, such as in thermal imaging.

### Dependencies

The Multisensor Labeler uses a number of open source projects and libraries to work properly:

- OpenCV 3.4.2 or higher. We recommend using PyImageSearch's tutorials to help with this process, and compiling via source so you can use CUDA if available, as well as GTK3+:
- [OpenCV with CUDA]
- [OpenCV 3.4.2]
- [OpenCV 4 and Above]

The rest of the dependencies are covered in the requirements.txt file install as seen below in the code.

### Installation and run app

```sh
$ git clone https://github.com/sugey/multisensor-labeler
$ cd multisensor-labeler
$ pip install -r requirements.txt
$ python3 multi.py
```

### Usage Instructions

You will need to load the directories for each image sensor. The sensors' images should be named identically within their respective folders.

Then, you will need to load where you would like to save the images. This MUST be a separate folder then your images. Not only is this helpful for organization, but when you go to add these to your trainginand labeling set, it's just good form.

Next, click the `Sync Folders` button. This will load your images, and take you to the first unlabeled image in your set. Any images that don't have a matching image filename in the other folder will be deleted.

Go ahead and make your adjustments with your thresholds to begin your blob separation. A good place to start is setting our your maxes to 255, and then seeing how to move the mins. You'll see a third image pop up which represents the thresholded image mask.

When you think you have the item isolated, click on `Detect Blobs`, and you should see your bounding boxes appear. Click `Save Labels`when ready.

Labels are saved in the [Pascal VOC label format](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/). Currently, it defaults to saving the `Person` class and the bounding boxes `xmin, ymin, xmax, ymax`.

If the bounding boxes are off at all, you can change the boxes manually. Start by changing the sensor2 boxes and then clicking on `Calc S2 Boxes Manually`. This will adjust the bounding boxes in both images. You MUST use the sensor 2 bounding boxes as the source of truth.

The offsets are also easily modified between images. You can change the default settings to whatever and they will automatically update when you click on `Detect Blobs` or `Calc S2 Boxes Manually` the next time.

### The Future

This needs a major UI upgrade, and some robustness. However, it is the only app currently that can isolate and label specific multi-sensor images at the same time.

PR requests are welcome.

### License

MIT LICENSE

Copyright 2019 Sugey, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[opencv with cuda]: https://www.pyimagesearch.com/2016/07/11/compiling-opencv-with-cuda-support/
[opencv 3.4.2]: https://www.pyimagesearch.com/2018/05/28/ubuntu-18-04-how-to-install-opencv/
[opencv 4 and above]: https://www.pyimagesearch.com/2018/08/15/how-to-install-opencv-4-on-ubuntu/
[numpy]: https://scipy.org/install.html
[natsort]: https://natsort.readthedocs.io/en/master/intro.html#installation
