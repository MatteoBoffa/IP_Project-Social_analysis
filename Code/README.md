# Presented Pipeline

This starts with the [downloading phase](https://github.com/MatteoBoffa/IP_Project-Social_analysis/tree/main/Code/Database_Material): with the aid of developers tools such as Instaloader and Flickr-api, it is possible to download the social contents of 
the chosen zone and period. 

After comes the clustering phase: each picture is clustered according to its geographical proximity with the others in order to achieve the dynamic zoning of the area under analysis.

Next, the classification phase: the Inception V3 architecture is used to classify the downloaded images. A script is then used to group the identified micro-classes into bigger ones.

Finally, the post-process phase, where different form of analysis are performed on the results of the previous steps.

![alt text](https://github.com/MatteoBoffa/IP_Project-Social_analysis/blob/main/Code/pipeline.jpg)
