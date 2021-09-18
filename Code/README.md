This folder collects the code of the presented pipeline. 

This start with the downloading phase: with the aid of developers tools such as Instaloader and Flickr-api, it is possible to download the social contents of 
chosen zone and period. 

After comes the clustering phase: each picture is clustered according to its geographical proximity with the others in order to achieve the dynamic zoning of the area under analysis.

Next, the classification phase: the Inception V3 architecture is used to classify the downloaded images. A script is then used to group the identified micro-classes into bigger ones.

Finally, the post-process phase, where different form of analysis are performed on the results of the previous steps.

![alt text](http://url/to/img.png)
