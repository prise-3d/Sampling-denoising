# main imports
import sys, os
import argparse
import numpy as np
import random

# image processing imports
from PIL import Image


# other params
output_data_file_name = 'pixels_data.csv'


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


def get_adjacents_chanels(image, max_width, max_height, w, h, c):
    
    chanels_values_list = []

    # get left pixel data
    if (h - 1) >= 0:
        chanels_values_list.append(image[w][h - 1][c] / 255.)

    # get top pixel data
    if (w - 1) >= 0:
        chanels_values_list.append(image[w - 1][h][c] / 255.)

    # get rifht pixel data
    if (h + 1) < max_height:
        chanels_values_list.append(image[w][h + 1][c] / 255.)

    # get left pixel data
    if (w + 1) < max_width:
        chanels_values_list.append(image[w + 1][h][c] / 255.)

    return chanels_values_list


def get_neighbord_chanels(image, max_width, max_height, w, h, c):

    chanels_values_list = []
    
    for dw in range(w-1, w+2): 
        for dh in range(h-1, h+2): 
            
            # get neighbors only
            if dw != w or dh != h: 

                # check out of bounds
                if (dw >= 0 and dw < max_width) and (dh >= 0 and dh < max_height):
                    chanels_values_list.append(image[dw][dh][c] / 255.)

    return chanels_values_list


def get_remote_neighbors_channels(image, max_width, max_height, w, h, c):

    chanels_values_list = []

    for dw in range(w-2, w+3):
        for dh in range(h-2, h+3): 

            # get remote neighbors only
            if dw not in [w, w - 1, w + 1] or dh not in [h, h - 1, h + 1]:

                # check out of bounds
                if (dw >= 0 and dw < max_width) and (dh >= 0 and dh < max_height):
                    chanels_values_list.append(image[dw][dh][c] / 255.)

    return chanels_values_list



def main():

    parser = argparse.ArgumentParser(description="Output data file")

    parser.add_argument('--folder', type=str, help="folder with each expected image")
    parser.add_argument('--reference', type=str, help="reference folder")
    parser.add_argument('--min', type=int, help="minimum samples to take care when generating data")
    parser.add_argument('--max', type=int, help="maximum samples to take care when generating data")
    parser.add_argument('--nb', type=int, help="number of generated images by scene (using `min` and `max` samples)")
    parser.add_argument('--output', type=str, help='output folder where pxels scenes data will be saved')
    

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

        # get scene folder path
        scene_folder = os.path.join(p_folder, scene)

        output_folder_path = os.path.join(p_output, scene)

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        outfile_path = os.path.join(output_folder_path, output_data_file_name)

        # check if file already exist and add missing pixels
        nb_pixels = 0

        if os.path.exists(outfile_path):
            with open(outfile_path, 'r') as f:
                nb_pixels = len(f.readlines())

            print('`' + outfile_path + '` was already generated, (stopped at pixel n°' + str(nb_pixels) + ') check if necessary to continue...')

            # open in append mode
            f = open(outfile_path, 'a')
        else:
            f = open(outfile_path, 'w')
        
        # get all samples images path
        samples_images = os.listdir(scene_folder)
        samples_images_path = [ os.path.join(scene_folder, img) for img in samples_images ]

        current_nb_pixels = 0

        for _ in range(p_nb):

            # get number of samples for each data generated
            nb_samples = random.randint(p_min, p_max)

            # shuffle list of images path and get `nb_samples` fist images path
            random.shuffle(samples_images_path)

            # get only the `nb_samples` first images path
            samples_path = samples_images_path[:nb_samples]

            img_list = []

            for img_path in samples_path:

                sample_img = Image.open(img_path)
                img_list.append(np.array(sample_img))


            width, height, chanels = img_list[0].shape
            
            for w in range(width):
                for h in range(height):

                    # increase number of pixels
                    current_nb_pixels = current_nb_pixels + 1

                    if current_nb_pixels < nb_pixels:
                        continue
                    
                    data_line = ""
                    # get reference pixels values
                    for c in range(chanels):
                        # write reference pixel values
                        data_line = data_line + str(reference_img[w, h, c] / 255.) + ';'
                        
                    # get `x` data from samples images
                    for index, c in enumerate(range(chanels)):
                        
                        current_pixel_samples = []
                        adjacent_pixels_samples = []
                        neighbors_pixels_samples = []
                        remote_neighbors_pixels_samples = []

                        for l in img_list:

                            # get chanel value
                            current_pixel_samples.append(l[w, h, c] / 255.)

                            # get adjacent pixels (for current chanel)
                            adjacent_pixels_samples.extend(get_adjacents_chanels(l, width, height, w, h, c))

                            # get neighbors pixels (for current chanel)
                            neighbors_pixels_samples.extend(get_neighbord_chanels(l, width, height, w, h, c))

                            # get remote neighbors pixels (for current chanel)
                            remote_neighbors_pixels_samples.extend(get_remote_neighbors_channels(l, width, height, w, h, c))
                        
                        # from current pixels
                        pixel_mean = np.mean(current_pixel_samples)
                        pixel_std = np.std(current_pixel_samples)

                        # from adjacent pixels
                        adj_pixels_mean = np.mean(adjacent_pixels_samples)
                        adj_pixels_std = np.std(adjacent_pixels_samples)

                        # from neighbors pixels
                        neighbors_pixels_mean = np.mean(neighbors_pixels_samples)
                        neighbors_pixels_std = np.std(neighbors_pixels_samples)

                        # from remote neighbors pixels
                        r_neighbors_pixels_mean = np.mean(remote_neighbors_pixels_samples)
                        r_neighbors_pixels_std = np.std(remote_neighbors_pixels_samples)


                        # write into data line
                        data_line = data_line + str(pixel_mean) + ';'
                        data_line = data_line + str(pixel_std) + ';'

                        data_line = data_line + str(adj_pixels_mean) + ';'
                        data_line = data_line + str(adj_pixels_std) + ';'

                        data_line = data_line + str(neighbors_pixels_mean) + ';'
                        data_line = data_line + str(neighbors_pixels_std) + ';'

                        data_line = data_line + str(r_neighbors_pixels_mean) + ';'
                        data_line = data_line + str(r_neighbors_pixels_std)

                        # if last element of line we do not add `;` char
                        if index < chanels - 1:
                            data_line = data_line + ';'

                    # first three values are `y` rgb references values, the others the `x` data
                    data_line = data_line + '\n'
                    f.write(data_line)                

            write_progress((image_counter + 1) / max_image_read)
            image_counter = image_counter + 1

        f.close()



if __name__ == "__main__":
    main()