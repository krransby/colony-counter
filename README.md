<!-- DEMO -->
<details open="open">
  <summary>Demo of the script running</summary>
  <img src="demo/hough_demo.gif" width="45%" title="Demo of the Hough Circle Method"> <img src="demo/water_demo.gif" width="45%" title="Demo of the Watershed Method">
</details>
<details>
  <summary>Script output images</summary>
  <img src="demo/hough_ex.png" width="45%" title="Hough Circle output image"> <img src="demo/water_ex.png" width="45%" title="Watershed output image">
</details>


<!-- ABOUT THE PROJECT -->
## About The Project


This repository contains the scrypt, data and outputs used in my project for the COSC428: Comuter Vision paper at the University of Canterbury (21S1).

The University of Canterbury internal paper can be found [here](https://krransby.github.io/media/COSC428.pdf) for more context.

**TL;DR:** This project proposes a method to aid in the enumeration of bacterial colonies present on agar plates through use of preprocessing techniques, the Hough Circle Transform and the Watershed Transform.



<!-- PREREQUISITES -->
## Prerequisites

This project was built on Python 3.8.18 with the following requirements: 
- numpy 1.20.1
- OpenCV 4.5.1.48
- screeninfo 0.8.1 (and its associated requirements)

All of which are specified in requirements.txt, and can be installed using the following command:

```bash
pip install -r requirements.txt
```


<!-- USAGE EXAMPLES -->
## Usage

Once you have a local copy of the repository, place images of the agar plates in the images/ directory

To run the scrypt, use the following command

  ```sh
  python counter.py <input-file> <method-to-use>
  ```

The supported methods are:
* **h**: Hough Circle Transform.
* **w**: Watershed Transform.


The input file is assumed to be in the images/ directory, so you don't have to include the directory in the filename.

For example, when using *"plate1.jpg"* you don't need to run the scrypt with *images/plate1.jpg*, just *plate1.jpg*.

Like so:

  ```sh
  python counter.py plate1.jpg h
  ```

If you'd prefer not to use the console, you can use the following call to main:

```python
if __name__ == '__main__':

    # Uncomment this line if not running through terminal,
    # only change the second and third elements
    main(['counter.py', 'plate1.jpg', 'h'])

    #main(sys.argv)
```

The script will run the same using this method, whatever is easier.

Once you have run the script, a window will appear for you to interact with as shown in the demos.

In order to progress from one "screen" to the next, press any key on your keyboard.

Outputs will be saved into the 'outputs/' directory with the following naming convention: "\<input-file\>\_\<method-to-use\>\_C\<number-of-colonies\>.png"

>**PLEASE NOTE:** Due to limitations with OpenCV's window scailing, the resolution of your images will be limited to whichever of the following is smallest:
>- The original size of the image
>- 980 pixels
>- The smallest dimension of all of displayes currently connected to the system.
>
>This is due to the fact that OpenCV's window size is dependent on the resolution of the image passed to `cv2.imshow()`.
>
>Note that the original results were achieved with a static scale of 980.

<!-- CONTACT -->
## Contact

Kayle Ransby - krr39@uclive.ac.nz

Source Code Link: [https://github.com/krransby/colony-counter](https://github.com/krransby/colony-counter)

Report Link: [Here](https://krransby.github.io/media/COSC428.pdf)




<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [University of Canterbury](https://www.canterbury.ac.nz/)
* [Richard Green (Supervisor)](https://www.canterbury.ac.nz/engineering/contact-us/people/richard-green.html)
* [images/HQ](http://opencfu.sourceforge.net/samples.php)
* [plate1.jpg](https://www.fishersci.se/shop/products/malt-extract-agar-contact-plate/10026782)
* [plate2.jpg](https://www.fishersci.se/shop/products/malt-extract-agar-4/10168882)
