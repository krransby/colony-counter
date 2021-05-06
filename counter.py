#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Purpose: COSC428 Project 2021

    Title: Automated Bacterial Colony Enumeration

    Source: https://github.com/krransby/colony-counter
"""

__author__ = "Kayle Ransby - 34043590"
__credits__ = ["Kayle Ransby", "Richard Green"]
__version__ = "3.1.0"
__license__ = "MIT"

# Imports

import sys
import time
from csv import writer
import cv2
import numpy as np

# "Globals"

# Colour used to identify colonies
houghColor = (0, 0, 255)

# Function for outputing images
output_image = (lambda n, v: cv2.imwrite('outputs/' + n + '.png', v))

# Debugging and output controls
DEBUG = False
OUTPUTDATA = False


def preprocess_image(img_ori):
    """
    Preprocesses the input image so that it can be used in the different algorithms.
    @param img_ori: Original input image.
    @Returns: (original image - cropped, preprocessed image).
    """

    # Kernal to be used for strong laplace filtering
    kernal_strong = np.array([
        [1, 1, 1],
        [1, -8, 1],
        [1, 1, 1]],
        dtype=np.float32)

    # Kernal to be used for weak laplace filtering
    kernal_weak = np.array([
        [0, 1, 0],
        [1, -4, 1],
        [0, 1, 0]],
        dtype=np.float32)

    # Perform laplace filtering
    img_lap = cv2.filter2D(img_ori, cv2.CV_32F, kernal_weak)
    img_sharp = np.float32(img_ori) - img_lap

    # Save the sharpened image
    if DEBUG:
        output_image("sharpened.png", img_sharp)

    # Convert to 8bits gray scale
    img_sharp = np.clip(img_sharp, 0, 255).astype('uint8')
    img_gray = cv2.cvtColor(img_sharp, cv2.COLOR_BGR2GRAY)

    # Save the greyscale image
    if DEBUG:
        output_image("greyscale.png", img_gray)

    # Binarize the greyscale image
    _, img_bin = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Save the binary image
    if DEBUG:
        output_image("binary.png", img_bin)

    # Remove noise from the binary image
    img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, np.ones((3, 3), dtype=int))

    # Save the noise reduced binary image
    if DEBUG:
        output_image("noise_reduction.png", img_bin)

    # Find the circular plate mask in the image
    plate_mask, circle = find_plate(img_ori, img_bin)

    cv2.circle(img_ori, (int(circle[0]), int(circle[1])), int(circle[2]), houghColor, 2)

    # Crop the original image if needed
    img_ori = crop_image(img_ori, circle)

    # If the number of white pixels is greater than the number of black pixels
    # i.e. attempt to automatically detect the mask colour
    inv = 0
    if np.sum(img_bin == 255) > np.sum(img_bin == 0):
        inv = 1

    # Create the GUI elements
    window_name = 'Colour adjustment'
    cv2.namedWindow(window_name)
    cv2.createTrackbar("Invert Plate", window_name, 0, 1, nothing)
    cv2.createTrackbar("Invert Mask", window_name, 0, 1, nothing)
    cv2.createTrackbar("Process more", window_name, 0, 1, nothing)

    # Set default parameters
    cv2.setTrackbarPos("Invert Plate", window_name, inv)
    cv2.setTrackbarPos("Invert Mask", window_name, inv)
    cv2.setTrackbarPos("Process more", window_name, 0)

    # Loop to keep the window open
    while True:
        # Read the parameters from the GUI
        inv = cv2.getTrackbarPos('Invert Plate', window_name)
        mask_inv = cv2.getTrackbarPos('Invert Mask', window_name)
        extra_processing = cv2.getTrackbarPos('Process more', window_name)

        img_pro = np.copy(img_bin)

        # Apply circular mask
        img_pro[(plate_mask == False)] = 255 * mask_inv

        # Crop the processed image if needed
        img_pro = crop_image(img_pro, circle)

        # Apply extra processing if needed
        if extra_processing == 1:
            img_pro = cv2.erode(img_pro, None)
            img_pro = cv2.dilate(img_pro, None)
            img_pro = cv2.erode(img_pro, None)

        # Invert the colours of the image, or not
        if inv == 0:
            img_show = img_pro
        elif inv == 1:
            img_show = cv2.bitwise_not(img_pro)

        # Display the image in the window
        cv2.imshow(window_name, img_show)

        # close the window
        if cv2.waitKey(100) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    # Save the preprocessed image
    if DEBUG:
        output_image("preprocessed.png", img_show)

    # Return the (cropped) original image and processed image
    return img_ori, img_show


def find_plate(img_ori, img_bin):
    """
    Identifies the plate with input from the user using the Hough Circle Transform.
    @param img_ori: Original image.
    @param img_bin: Binary thresholded image.
    @Returns: (Plate mask, circle).
    """

    # Define the max possible plate radius as
    # half the image size
    max_possible_radius = int(min(img_bin.shape) / 2)
    circle = 0

    # Create the GUI elements
    window_name = 'Plate Identification'
    cv2.namedWindow(window_name)
    cv2.createTrackbar("Plate Radius", window_name, 0, 50, nothing)
    cv2.createTrackbar("Radius offset", window_name, 0, 200, nothing)

    # Set default parameters
    cv2.setTrackbarPos("Plate Radius", window_name, 25)
    cv2.setTrackbarPos("Radius offset", window_name, 100)

    # Loop to keep the window open
    while True:
        # Read the parameters from the GUI
        radius_scale = cv2.getTrackbarPos('Plate Radius', window_name) / 100
        max_radius = int((max_possible_radius * radius_scale) + (max_possible_radius * 0.5))
        min_radius = max_radius - 10

        radius_offset = cv2.getTrackbarPos('Radius offset', window_name) / 100

        # Find plate in the image with Hough Circle Transform
        circles = cv2.HoughCircles(img_bin, cv2.HOUGH_GRADIENT, 1, 20, param1=100,
                                    param2=10, minRadius=min_radius, maxRadius=max_radius)

        img_show = img_ori.copy()

        if circles is not None:

            # Return data of the smallest circle found
            circles = (circles[0, :]).astype("float")
            max_c = np.argmax(circles, axis=0)
            indx = max_c[2]
            circle = circles[indx]
            circle = (int(circle[0]), int(circle[1]), int(radius_offset * circle[2]))

            # Draw the outer circle
            cv2.circle(img_show, (circle[0], circle[1]), circle[2], houghColor, 2)

            # Draw the center of the circle
            cv2.circle(img_show, (circle[0], circle[1]), 2, houghColor, 3)

        cv2.imshow(window_name, img_show)

        # Close the window
        if cv2.waitKey(100) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    # Create plate mask:
    plate_mask = np.zeros(img_bin.shape, np.uint8)
    plate_mask = cv2.circle(plate_mask, (circle[0], circle[1]), circle[2], (255, 255, 255),
                            thickness=-1)

    return plate_mask, circle


def watershed_method(img_ori, img_pro):
    """
    Colony identification using watershed transform.
    @param img_ori: Original image.
    @param img_pro: Processed image.
    @Returns: (output image, no. colonies).
    """

    # Create the border of the components
    border = cv2.dilate(img_pro, None)
    border = border - cv2.erode(border, None)

    # Create the seed(s) for the watershed transform
    dist = cv2.distanceTransform(img_pro, 2, 3)
    dist = ((dist - dist.min()) / (dist.max() - dist.min()) * 255).astype(np.uint8)
    _, dist = cv2.threshold(dist, 110, 255, cv2.THRESH_BINARY)

    # Find the markers for the watershed transform
    num_components, markers = cv2.connectedComponents(dist)

    # Completing the markers
    markers = markers * (255 / (num_components + 1))
    markers[border == 255] = 255
    markers = markers.astype(np.int32)

    # Perfoming the watershead transform
    cv2.watershed(img_ori, markers)

    # Make the markers pretty and apply them to the input image
    markers[markers == -1] = 0
    markers = markers.astype(np.uint8)
    result = 255 - markers
    result[result != 255] = 0
    result = cv2.dilate(result, None)
    img_ori[result == 255] = houghColor

    return img_ori, num_components - 1


def hough_circle_method(img_ori, img_pro):
    """
    Colony identification using Hough Circle transform.
    @param img_ori: Original image.
    @param img_pro: Processed image.
    @Returns: (output image, no. colonies).
    """

    # Create the GUI elements
    window_name = 'Hough Circle Transform'
    cv2.namedWindow(window_name)
    cv2.createTrackbar('Sensitivity', window_name, 0, 10, nothing)
    cv2.createTrackbar('Neighborhood', window_name, 0, 30, nothing)
    cv2.createTrackbar('Accumulator', window_name, 1, 50, nothing)
    cv2.createTrackbar("Min Radius", window_name, 0, 30, nothing)
    cv2.createTrackbar("Max Radius", window_name, 0, 30, nothing)

    # Set some default parameters
    cv2.setTrackbarPos("Sensitivity", window_name, 0)
    cv2.setTrackbarPos("Neighborhood", window_name, 20)
    cv2.setTrackbarPos("Accumulator", window_name, 20)
    cv2.setTrackbarPos("Min Radius", window_name, 15)
    cv2.setTrackbarPos("Max Radius", window_name, 15)

    # Loop to keep the window open
    while True:
        # Read the parameters from the GUI
        sensitivity = cv2.getTrackbarPos('Sensitivity', window_name)
        nhood = cv2.getTrackbarPos('Neighborhood', window_name)
        param2 = cv2.getTrackbarPos('Accumulator', window_name)
        min_radius = cv2.getTrackbarPos('Min Radius', window_name)
        max_radius = cv2.getTrackbarPos('Max Radius', window_name)

        # Find circles is the image with Hough Circle Transform
        circles = cv2.HoughCircles(img_pro, cv2.HOUGH_GRADIENT, sensitivity+1, nhood+1, param1=100,
                                    param2=param2+1, minRadius=min_radius+1, maxRadius=max_radius+1)

        img_show = img_ori.copy()

        if circles is not None:
            circles = np.uint16(np.around(circles))

            for i in circles[0,:]:
                # Draw the outer circle
                cv2.circle(img_show, (i[0], i[1]), i[2], houghColor, 2)


        cv2.imshow(window_name, img_show)

        # close the window
        if cv2.waitKey(100) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    return img_show, len(circles[0])


def nothing(_):
    """
    Callback function for the createTrackbar function;
    this does nothing.
    @param x: no purpose.
    """

    pass # Nothing


def error(message, code=0):
    """
    function for throwing cleaner error messages + codes;
    preferable to throwing exceptions.
    @param message: String to be printed on error.
    @param code: scrypt exit code (default = 0).
    """

    print("Error:", message)
    sys.exit(int(code))


def load_image(filename, desired_res):
    """
    Function to load in an input image and set the width to
    the value specified in the parameter "desired_res".
    @param filename: String, file to be opened within the 'images/' directory.
    @param desired_res: Int., defired resolution of the input image (horizontal).
    @Returns: Scaled input image.
    """

    # Load the image
    img_ori = cv2.imread('images/' + filename)

    # Error checking
    if img_ori is None:
        error('Could not open or find the image: "{}".'.format(filename), 1)

    # Resize the image to the specified size
    scale = (desired_res / img_ori.shape[1])
    img_ori = cv2.resize(img_ori, (int(img_ori.shape[1] * scale), int(img_ori.shape[0] * scale)))

    return img_ori


def crop_image(img, mask):
    """
    Crops the given image by fitting a bounding box using
    the given circular mask; This makes the output more
    presentable.
    @param img: Image to be cropped.
    @param mask: Circular mask retrieved from Hough Transform.
    @Returns: Cropped (hopefully square) input image.
    """

    output = img

    # if the height is greater than the width;
    # i.e. portrait image
    if img.shape[0] > img.shape[1]:

        # Retrieve the coordinates & radius from circular mask
        x_pos, y_pos, radius = mask

        # Find the coordinates for the bottom left & top right of box
        x_bot = int(x_pos - radius)    # Bottom Left X
        y_bot = int(y_pos - radius)    # Bottom Left Y
        x_top = int(x_pos + radius)    # Top Right X
        y_top = int(y_pos + radius)    # Top Right Y

        # Find min distance from the edge of the box to the image border
        min_x_dist = min((img.shape[1] - x_top), (img.shape[1] - (img.shape[1] - x_bot)))
        min_y_dist = min((img.shape[0] - y_top), (img.shape[0] - (img.shape[0] - y_bot)))
        min_dist = min(min_x_dist, min_y_dist)

        # Apply remainder
        x_bot = (x_bot - min_dist)    # Bottom Left X
        y_bot = (y_bot - min_dist)    # Bottom Left Y
        x_top = (x_top + min_dist)    # Top Right X
        y_top = (y_top + min_dist)    # Top Right Y

        # Crop image using the new mask
        output = output[y_bot:y_top, x_bot:x_top]

    return output


def generate_output(img, count, method, filename, period):
    """
    Creates a fancy output image containing the processed image,
    the filename, the method used and the number of colonies
    found.
    @param img: Processed image.
    @param count: Number of colonies identified.
    @param method: Transform used to generate output.
    @param filename: Name of the file we just processed.
    @param period: Time taken (in seconds).
    @Returns: Finalized output image.
    """

    # For converting argument to text
    methods = {
        'h': 'Hough Circle Transform',
        'w': 'Watershed Transform'
    }

    # Font to use in output image
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scl = 0.5
    font_col = (0, 0, 0)

    # Create black border:
    height, width, chan = img.shape
    border_size = 20
    image_height = height + (border_size + 100)
    image_width = width + border_size
    border = np.zeros((image_height, image_width, chan), np.uint8)
    border[:,0:image_width] = houghColor

    # Process filename:
    name = filename.split("/")[-1].split(".")[0]

    # Generate text for image
    # Filename string
    file_str = 'File: "{}"'.format(name)
    cv2.putText(border, file_str, (10, image_height-80), font, font_scl, font_col, 1, cv2.LINE_AA)

    # Method used string
    method_str = 'Method: {}'.format(methods[method.lower()])
    cv2.putText(border, method_str, (10, image_height-60), font, font_scl, font_col, 1, cv2.LINE_AA)

    # Number of colonies string
    count_str = 'Colonies: {}'.format(count)
    cv2.putText(border, count_str, (10, image_height-40), font, font_scl, font_col, 1, cv2.LINE_AA)

    # Amount of time string
    time_str = 'Time: {0:.2f} s'.format(period)
    cv2.putText(border, time_str, (10, image_height-20), font, font_scl, font_col, 1, cv2.LINE_AA)

    # Place output image into the border
    border[10:10+height, 10:10+width] = img

    # Save the output file
    output_image('{}_{}_C{}'.format(name, method, count), border)

    # Save data to .csv file
    if OUTPUTDATA:
        # csv file format
        data = [name, period, count, method]

        # Open our existing CSV file in append mode
        # Create a file object for this file
        with open('data_UC_water.csv', 'a') as f_object:

            # Pass this file object to csv.writer()
            # and get a writer object
            writer_object = writer(f_object)

            # Pass the list as an argument into
            # the writerow()
            writer_object.writerow(data)

            # Close the file object
            f_object.close()

    return border


def main(args):
    """
    Main execution function
    @Param args: Command line arguments.
    """

    # Check if we have the correct number of arguments
    if len(args) != 3:
        error('Incorrect number of arguments. Usage: counter.py <file> <method>', 1)

    # Load the specified image
    img_ori = load_image(args[1], 980)

    # Start counting the time spent counting
    start_time = time.time()

    # Preprocess the input image
    img_ori, img_pro = preprocess_image(img_ori)

    # Run specified transform method
    if args[2].lower() == 'w':
        output, colonies = watershed_method(img_ori, img_pro)

    elif args[2].lower() == 'h':
        output, colonies = hough_circle_method(img_ori, img_pro)

    else:
        error('Undefined detection method: "{}"'.format(args[2]), 1)

    # Generate the output
    output = generate_output(output, colonies, args[2], args[1], (time.time() - start_time))

    # Visualize the final image
    cv2.imshow('Final Result: {} Colonies found'.format(colonies), output)
    cv2.waitKey()


if __name__ == '__main__':

    # Uncomment this line if not running through terminal,
    # only change the second and third elements
    main(['counter.py', 'plate2.jpg', 'w'])

    #main(sys.argv)
