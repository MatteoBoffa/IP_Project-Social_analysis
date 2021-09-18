# Presented Pipeline


This start with the [downloading phase](https://github.com/MatteoBoffa/IP_Project-Social_analysis/tree/main/Code/Downloading): with the aid of developers tools such as Instaloader and Flickr-api, it is possible to download the social contents of 
chosen zone and period. 

After comes the [clustering phase](https://github.com/MatteoBoffa/IP_Project-Social_analysis/tree/main/Code/Clustering): each picture is clustered according to its geographical proximity with the others in order to achieve the dynamic zoning of the area under analysis.

Next, the [classification phase](https://github.com/MatteoBoffa/IP_Project-Social_analysis/tree/main/Code/Classifying): the Inception V3 architecture is used to classify the downloaded images. A script is then used to group the identified micro-classes into bigger ones.

Finally, the [post-process phase](https://github.com/MatteoBoffa/IP_Project-Social_analysis/tree/main/Code/Post_process), where different form of analysis are performed on the results of the previous steps.

![alt text](https://github.com/MatteoBoffa/IP_Project-Social_analysis/blob/main/Code/pipeline.jpg)
