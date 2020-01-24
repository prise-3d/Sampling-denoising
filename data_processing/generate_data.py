# main imports
import sys, os
import argparse
import numpy as np
import random

# image processing imports
from PIL import Image


'''
Display progress information as progress bar
'''
def write_progress(progress):
    barWidth = 180

    output_str = "["
    pos = barWidth * progress
    for i in range(barWidth):
        if i < pos:
           output_str = output_str + "="
        elif i == pos:
           output_str = output_str + ">"
        else:
            output_str = output_str + " "

    output_str = output_str + "] " + str(int(progress * 100.0)) + " %\r"
    print(output_str)
    sys.stdout.write("\033[F")


def get_adjacents_pixels(image, i, j, k):
    
    pixels_list = []

def main():

    parser = argparse.ArgumentParser(description="Output data file")

    parser.add_argument('--folder', type=str, help="folder with each expected image")
    parser.add_argument('--reference', type=str, help="reference folder")
    parser.add_argument('--min', type=int, help="minimum samples to take care when generating data")
    parser.add_argument('--max', type=int, help="maximum samples to take care when generating data")
    parser.add_argument('--nb', type=int, help="number of generated images by scene (using `min` and `max` samples)")
    parser.add_argument('--output', type=str, help='save entropy for each zone of each scene into file')
    

    args = parser.parse_args()

    p_folder    = args.folder
    p_reference = args.reference
    p_min       = args.min
    p_max       = args.max
    p_nb        = args.nb
    p_output    = args.output


    scenes_folder = os.listdir(p_folder)

    # progress information
    max_image_read = len(scenes_folder) * p_nb
    image_counter = 0


    for scene in scenes_folder:

        # get reference images information
        reference_scene_folder = os.path.join(p_reference, scene)
        reference_img_path = os.path.join(reference_scene_folder, os.listdir(reference_scene_folder)[0])
        reference_img = np.array(Image.open(reference_img_path))

        scene_folder = os.path.join(p_folder, scene)
        
        samples_images = os.listdir(scene_folder)
        samples_images_path = [ os.path.join(scene_folder, img) for img in samples_images ]

        for _ in range(p_nb):

            nb_samples = random.randint(p_min, p_max)

            # shuffle list of images path and get `nb_samples` fist images path
            random.shuffle(samples_images_path)

            samples_path = samples_images_path[:nb_samples]

            img_list = []

            for img_path in samples_path:

                sample_img = Image.open(img_path)
                img_list.append(np.array(sample_img))


            width, height, chanels = img_list[0].shape
            
            for i in range(width):
                for j in range(height):
                    
                    data_line = ""
                    # get reference pixels values
                    for k in range(chanels):
                        # write reference pixel values
                        data_line = data_line + str(reference_img[i, j, k] / 255.) + ';'
                        
                    # get `x` data from samples images
                    for k in range(chanels):
                        
                        current_pixel_samples = []
                        adjacent_pixels_samples = []

                        for l in img_list:

                            # get chanel value
                            current_pixel_samples.append(l[i,j,k] / 255.)
                        
                        pixel_mean = np.mean(current_pixel_samples)
                        pixel_std = np.std(current_pixel_samples)

                        # write into data line
                        data_line = data_line + str(pixel_mean) + ';'
                        data_line = data_line + str(pixel_std)c + ';'

                

            write_progress((image_counter + 1) / max_image_read)
            image_counter = image_counter + 1



if __name__ == "__main__":
    main()