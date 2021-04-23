#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Kayle Ransby - 34043590"
__credits__ = ["Kayle Ransby", "Richard Green"]
__version__ = "3.0.0"
__maintainer__ = "Kayle Ransby"
__email__ = "krr39@uclive.ac.nz"
__status__ = "Release 1"


# Imports

import cv2
import numpy as np
import sys
import time
from csv import writer

# "Globals"

houghColor = (0, 0, 255) # colour used to identify colonies

# function for outputing images
output_image = (lambda n, v: cv2.imwrite('outputs/' + n + '.png', v))


def preprocessImage(imgOri):
    """
    Preprocesses the input image so that it can be used in the different algorithms.
    @param imgOri: Original input image.
    @Returns: (original image - cropped, preprocessed image).
    """

    # Kernal to be used for strong laplace filtering
    lapStrong = np.array([
        [1, 1, 1], 
        [1, -8, 1], 
        [1, 1, 1]], 
        dtype=np.float32)
    
    # Kernal to be used for weak laplace filtering
    lapWeak = np.array([
        [0, 1, 0], 
        [1, -4, 1], 
        [0, 1, 0]], 
        dtype=np.float32)

    
    # Perform laplace filtering
    imgLap = cv2.filter2D(imgOri, cv2.CV_32F, lapWeak)
    sharp = np.float32(imgOri)
    imgResult = sharp - imgLap

    # Convert back to 8bits gray scale
    imgResult = np.clip(imgResult, 0, 255)
    imgResult = imgResult.astype('uint8')
    imgGray = cv2.cvtColor(imgResult, cv2.COLOR_BGR2GRAY)

    # Binarize the greyscale image
    _, imgBin = cv2.threshold(imgGray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Remove noise from the binary image
    imgBin = cv2.morphologyEx(imgBin, cv2.MORPH_OPEN, np.ones((3, 3), dtype=int))

    # Find the circular plate mask in the image
    plateMask, circle = findPlate(imgOri, imgBin)

    cv2.circle(imgOri, (int(circle[0]), int(circle[1])), int(circle[2]), houghColor, 2)

    # Crop the original image if needed
    imgOri = crop_image(imgOri, circle)

    # If the number of white pixels is greater than the number of black pixels
    # i.e. attempt to automatically detect the mask colour
    mInv = 0
    if np.sum(imgBin == 255) > np.sum(imgBin == 0):
        mInv = 1

    # Create the GUI elements
    windowName = 'Colour adjustment'
    cv2.namedWindow(windowName)
    cv2.createTrackbar("Invert Plate", windowName, 0, 1, nothing)
    cv2.createTrackbar("Invert Mask", windowName, 0, 1, nothing)
    cv2.createTrackbar("Process more", windowName, 0, 1, nothing)

    # Set default parameters
    cv2.setTrackbarPos("Invert Plate", windowName, 0)
    cv2.setTrackbarPos("Invert Mask", windowName, mInv)
    cv2.setTrackbarPos("Process more", windowName, 0)

    # Loop to keep the window open
    while True:
        # Read the parameters from the GUI
        inv = cv2.getTrackbarPos('Invert Plate', windowName)
        mInv = cv2.getTrackbarPos('Invert Mask', windowName)
        extraProc = cv2.getTrackbarPos('Process more', windowName)

        imgPro = np.copy(imgBin)

        # Apply circular mask
        idx = (plateMask == False)
        imgPro[idx] = 255 * mInv

        # Crop the processed image if needed
        imgPro = crop_image(imgPro, circle)

        # Apply extra processing if needed
        if extraProc == 1:
            imgPro = cv2.erode(imgPro, None)
            imgPro = cv2.dilate(imgPro, None)
            imgPro = cv2.erode(imgPro, None)

        # Invert the colours of the image, or not
        if inv == 0:
            imgShow = imgPro
        elif inv == 1:
            imgShow = cv2.bitwise_not(imgPro)

        # Display the image in the window
        cv2.imshow(windowName, imgShow)

        # close the window
        if cv2.waitKey(100) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    # Return the (cropped) original image and processed image
    return imgOri, imgShow


def findPlate(imgOri, imgBin):
    """
    Identifies the plate with input from the user using the Hough Circle Transform.
    @param imgOri: Original image.
    @param imgBin: Binary thresholded image.
    @Returns: (Plate mask, circle).
    """
    
    # Define the max possible plate radius as
    # half the image size
    maxPossibleRadius = int(min(imgBin.shape) / 2)
    circle = 0

    # Create the GUI elements
    windowName = 'Plate Identification'
    cv2.namedWindow(windowName)
    cv2.createTrackbar("Plate Radius", windowName, 0, 50, nothing)
    cv2.createTrackbar("Radius offset", windowName, 0, 200, nothing)

    # Set default parameters
    cv2.setTrackbarPos("Plate Radius", windowName, 25)
    cv2.setTrackbarPos("Radius offset", windowName, 100)

    # Loop to keep the window open
    while True:
        # Read the parameters from the GUI
        param1 = 100 # Canny
        param2 = 10  # Accum
        maxRadius = int((maxPossibleRadius * (cv2.getTrackbarPos('Plate Radius', windowName) / 100))
         + (maxPossibleRadius * 0.5))
        
        minRadius = maxRadius - 10
        radiusOffset = cv2.getTrackbarPos('Radius offset', windowName) / 100

        # Find plate in the image with Hough Circle Transform
        circles = cv2.HoughCircles(imgBin, cv2.HOUGH_GRADIENT, 1, 20, param1=param1,
                                    param2=param2, minRadius=minRadius, maxRadius=maxRadius)

        imgShow = imgOri.copy()

        if circles is not None:

            # Return data of the smallest circle found
            circles = (circles[0, :]).astype("float")
            max_c = np.argmax(circles, axis=0)
            indx = max_c[2]
            circle = circles[indx]
            circle = (int(circle[0]), int(circle[1]), int(radiusOffset * circle[2]))

            # Draw the outer circle
            cv2.circle(imgShow, (circle[0], circle[1]), circle[2], houghColor, 2)

            # Draw the center of the circle
            cv2.circle(imgShow, (circle[0], circle[1]), 2, houghColor, 3)

        cv2.imshow(windowName, imgShow)

        # Close the window
        if cv2.waitKey(100) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    # Create plate mask:
    plateMask = np.zeros(imgBin.shape, np.uint8)
    plateMask = cv2.circle(plateMask, (circle[0], circle[1]), circle[2], (255, 255, 255), thickness=-1)

    return plateMask, circle


def watershed(imgOri, imgPro):
    """
    Colony identification using watershed transform.
    @param imgOri: Original image.
    @param imgPro: Processed image.
    @Returns: (output image, no. colonies).
    """

    # Create the border of the components
    border = cv2.dilate(imgPro, None)
    border = border - cv2.erode(border, None)

    # Create the seed(s) for the watershed transform
    dist = cv2.distanceTransform(imgPro, 2, 3)
    dist = ((dist - dist.min()) / (dist.max() - dist.min()) * 255).astype(np.uint8)
    _, dist = cv2.threshold(dist, 150, 255, cv2.THRESH_BINARY)

    # Find the markers for the watershed transform
    noComponents, markers = cv2.connectedComponents(dist)

    # Completing the markers
    markers = markers * (255 / (noComponents + 1))
    markers[border == 255] = 255
    markers = markers.astype(np.int32)

    # Perfoming the watershead transform
    cv2.watershed(imgOri, markers)

    # Make the markers pretty and apply them to the input image
    markers[markers == -1] = 0
    markers = markers.astype(np.uint8)
    result = 255 - markers
    result[result != 255] = 0
    result = cv2.dilate(result, None)
    imgOri[result == 255] = houghColor

    return imgOri, noComponents - 1


def hough(imgOri, imgPro):
    """
    Colony identification using Hough Circle transform.
    @param imgOri: Original image.
    @param imgPro: Processed image.
    @Returns: (output image, no. colonies).
    """

    # Create the GUI elements
    windowName = 'Hough Circle Transform'
    cv2.namedWindow(windowName)
    cv2.createTrackbar('sensitivity', windowName, 0, 10, nothing)
    cv2.createTrackbar('n-hood', windowName, 0, 30, nothing)
    cv2.createTrackbar('Accumulator Threshold', windowName, 1, 50, nothing)
    cv2.createTrackbar("Min Radius", windowName, 0, 30, nothing)
    cv2.createTrackbar("Max Radius", windowName, 0, 30, nothing)

    # Set some default parameters
    #cv2.setTrackbarPos("Canny Threshold", windowName, 100)
    cv2.setTrackbarPos("sensitivity", windowName, 0)
    cv2.setTrackbarPos("n-hood", windowName, 20)
    cv2.setTrackbarPos("Accumulator Threshold", windowName, 20)
    cv2.setTrackbarPos("Min Radius", windowName, 15)
    cv2.setTrackbarPos("Max Radius", windowName, 15)

    # Loop to keep the window open
    while True:
        # Read the parameters from the GUI
        param1 = 100 # Canny
        sensitivity = cv2.getTrackbarPos('sensitivity', windowName)
        nhood = cv2.getTrackbarPos('n-hood', windowName)
        param2 = cv2.getTrackbarPos('Accumulator Threshold', windowName)
        minRadius = cv2.getTrackbarPos('Min Radius', windowName)
        maxRadius = cv2.getTrackbarPos('Max Radius', windowName)

        # Find circles is the image with Hough Circle Transform
        circles = cv2.HoughCircles(imgPro, cv2.HOUGH_GRADIENT, sensitivity+1, nhood+1, param1=param1+1,
                                    param2=param2+1, minRadius=minRadius+1, maxRadius=maxRadius+1)

        imgShow = imgOri.copy()

        if circles is not None:
            circles = np.uint16(np.around(circles))

            for i in circles[0,:]:
                # Draw the outer circle
                cv2.circle(imgShow, (i[0], i[1]), i[2], houghColor, 2)


        cv2.imshow(windowName, imgShow)

        # close the window
        if cv2.waitKey(100) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    return imgShow, len(circles[0])


def nothing(x):
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


def load_image(filename, desiredRes):
    """
    Function to load in an input image and set the width to
    the value specified in the parameter "desiredRes".
    @param filename: String, file to be opened within the 'images/' directory.
    @param desiredRes: Int., defired resolution of the input image (horizontal).
    @Returns: Scaled input image.
    """

    # Load the image
    imgOri = cv2.imread('images/' + filename)

    # Error checking
    if imgOri is None:
        error('Could not open or find the image: "{}".'.format(args[1]), 1)

    # Resize the image to the specified size
    scale = (desiredRes / imgOri.shape[1])
    imgOri = cv2.resize(imgOri, (int(imgOri.shape[1] * scale), int(imgOri.shape[0] * scale)))

    return imgOri


def crop_image(img, mask):
    """
    Crops the given image by fitting a bounding box using
    the given circular mask; This makes the output more 
    presentable.
    @param img: Image to be cropped.
    @param mask: Circular mask retrieved from Hough Transform.
    @Returns: Cropped (hopefully square) input image.
    """

    # By default images aren't cropped
    output = img

    # if the height is greater than the width;
    # i.e. portrait image
    if img.shape[0] > img.shape[1]:

        # Retrieve the coordinates & radius from circular mask
        x, y, r = mask

        # Create a square from the information above
        BLX = int(x - r)            # Bottom Left X
        RMD = BLX                   # Remainder to make image square

        BLX = int(BLX - RMD)        # Bottom Left X
        BLY = int((y - r) - RMD)    # Bottom Left Y
        TRX = int((x + r) + RMD)    # Top Right X
        TRY = int((y + r) + RMD)    # Top Right Y

        # Crop image using the new mask
        output = output[BLY:TRY, BLX:TRX]

    return output


def generate_output(img, count, method, filename, time):
    """
    Creates a fancy output image containing the processed image,
    the filename, the method used and the number of colonies
    found.
    @param img: Processed image.
    @param count: Number of colonies identified.
    @param method: Transform used to generate output.
    @param filename: Name of the file we just processed.
    @Returns: Finalized output image.
    """
    
    # For converting argument to text
    methods = {
        'h': 'Hough Circle Transform',
        'w': 'Watershed Transform'
    }

    # Font to use in output image
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.5
    fontCol = (0, 0, 0)
    
    # Create black border:
    height, width, chan = img.shape
    bWidth = 20
    imageHeight = height + (bWidth + 100)
    imageWidth = width + bWidth
    border = np.zeros((imageHeight, imageWidth, chan), np.uint8)
    border[:,0:imageWidth] = houghColor

    # Generate text for image
    # Filename string
    fileStr = 'File: "{}"'.format(filename)
    cv2.putText(border, fileStr, (10, imageHeight-80), font, fontScale, fontCol, 1, cv2.LINE_AA)

    # Method used string
    methodStr = 'Method: {}'.format(methods[method.lower()])
    cv2.putText(border, methodStr, (10, imageHeight-60), font, fontScale, fontCol, 1, cv2.LINE_AA)
    
    # Number of colonies string
    countStr = 'Colonies: {}'.format(count)
    cv2.putText(border, countStr, (10, imageHeight-40), font, fontScale, fontCol, 1, cv2.LINE_AA)

    # Amount of time string
    timeStr = 'Time: {0:.2f} s'.format(time)
    cv2.putText(border, timeStr, (10, imageHeight-20), font, fontScale, fontCol, 1, cv2.LINE_AA)

    # Place output image into the border
    border[10:10+height, 10:10+width] = img

    # Save the output file
    output_image('output_{}_C{}'.format(method, count), border)
  
    # csv file format
    List = [filename, time, count, method]
    
    # Open our existing CSV file in append mode
    # Create a file object for this file
    with open('data.csv', 'a') as f_object:
    
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)
    
        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(List)
    
        #Close the file object
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
    imgOri = load_image(args[1], 980)

    # Start counting the time spent counting
    startTime = time.time()

    # Preprocess the input image
    imgOri, imgPro = preprocessImage(imgOri)

    # Run specified transform method
    if args[2].lower() == 'w':
        output, colonies = watershed(imgOri, imgPro)

    elif args[2].lower() == 'h':
        output, colonies = hough(imgOri, imgPro)

    else:
        error('Undefined detection method: "{}"'.format(args[2]), 1)
    
    # Generate the output
    output = generate_output(output, colonies, args[2], args[1], (time.time() - startTime))

    # Visualize the final image
    cv2.imshow('Final Result: {} Colonies found'.format(colonies), output)
    cv2.waitKey()


if __name__ == '__main__':
    
    # Uncomment these lines if not running through terminal
    args = ['counter.py', 'plate2.jpg', 'w']
    main(args)

    #main(sys.argv)