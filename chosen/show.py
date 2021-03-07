from os import walk, path
import sys

import pygame

import pandas as pd
root_path='https://www.dropbox.com/home/Pictures_IP/Flickr_v2'
pred=pd.DataFrame()
df = pd.read_table('Flickr_final.xls')#use r before absolute file path 
ls=pd.DataFrame(df['ids,predictions,lat,lng,label,CLUSTER_ID'].str.split(',').tolist())
pred[['0','pred','2']]=pd.DataFrame(df['ids,predictions,lat,lng,label,CLUSTER_ID'].str.split('"').tolist())
df[['ids']]=pd.DataFrame(pred['0'].str.replace(',', ''))
df[['predictions']]=pd.DataFrame(pred['pred'])
pred['2']=pd.DataFrame(pred['2'].str[1:])

df[['lat', 'lng', 'label', 'CLUSTER_ID']]= pd.DataFrame(pred['2'].str.split(',').tolist())

cluster=19
label=1
list_of_img=[]
cnt=0
for index, row in df.iterrows() :
    #cnt+=1
    #print(cnt)
    if int(row['CLUSTER_ID'][:-2])==cluster and row['predictions']!='' and int(row['predictions'].split(':')[0][:-1])==label:
        list_of_img.append(row['ids'])
print(list_of_img)

'''

import cv2

img=cv2.imread('myimage.jpg',cv2.IMREAD_GRAYSCALE)

cv2.imshow('image',img)


while True:
    # Scan folder
    file_names = []
    for (dirpath, dirs, files) in walk(root_path):
        print(dirpath)

        file_names.extend([path.join(dirpath, f) for f in files if path.splitext(f)[1] in extensions])

    # Iterate over all paths, load images into memory
    images = []
    for img_file in file_names:
        try:
            images.append(pygame.image.load(img_file))
        except:
            pass

    #  Display the images for a short time
    for img in images:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
        # Center image on screen
        r = img.get_rect()
        screen.blit(img, r.move((width-r.w)/2, (height-r.h)/2))
        pygame.display.flip()
        pygame.time.wait(2000)
'''
