# Surfclass 🏄🌴
Turns Lidar-Data into a surface classified raster

Linux build: [![CircleCI](https://circleci.com/gh/Kortforsyningen/surfclass/tree/master.svg?style=svg)](https://circleci.com/gh/Kortforsyningen/surfclass/tree/master)

Windows build: [![Build status](https://ci.appveyor.com/api/projects/status/j2rju86qvrg8t5jy/branch/master?svg=true)](https://ci.appveyor.com/project/Septima/surfclass/branch/master)

# Installation

## Conda

```bash
git clone https://github.com/Septima/surfclass.git
cd surfclass
conda env create -n surfclass -f environment.yml
conda activate surfclass
pip install .
```


# Usage
Surfclass installs itself as a python module which can be called from the commandline or imported into existing python projects. The module can from the commandline be used to rasterize lidar files, prepare features, train a randomforest model, calculate a surface classified raster and assign class occurences to a vector layer. 

The commmandline tool comes with four main commands: `prepare`, `train`, `classify` and `extract`. 
After installing the module, type `surfclass --help` to see the following:

```
Usage: surfclass [OPTIONS] COMMAND [ARGS]...

  surfclass command line interface

Options:
  --version                       Show the version and exit.
  -v, --verbosity [CRITICAL|ERROR|WARNING|INFO|DEBUG]
                                  Set verbosity level
  --help                          Show this message and exit.

Commands:
  classify  Surface classify raster
  extract   Extract data from surfclass classified raster
  prepare   Prepare data for surfclass.
  train     Train surface classification models using path to training_data.
```

## Prepare
The prepare subcommands contains methods for *preparing* data for either training or classification of the RandomForest method. 

 ```
 Commands:
  lidargrid        Rasterize lidar data Rasterize one or more lidar files...
  extractfeatures  Extract statistical features from a raster file.
  traindata        Extracts training data defined by polygons with a class...
  traindatainfo    Shows basic information about extracted training data.
 ```
### `lidargrid`
lidargrid rasterizes an input lidar file in either `.las` or `.laz` format into grid cells. `lidargrid` can rasterize multiple dimensions from multiple files in one call. See `surfclass prepare lidargrid --help` for more information

#### Example: 
```
surfclass prepare lidargrid -srs epsg:25832 -b 721000 6150000 722000 6151000 -r 0.4 -d Amplitude -d Intensity input1.las input2.las c:\outdir\
```
### `extractfeatures`
extractfeatures extracts statistical features from a raster file, usually from output calculated with lidargrid. Extracts derived features, such as mean, difference of mean and variance. Uses a window of size -n to calculate neighborhood statistics for each cell in the input raster using a convolution-like sliding window. The output raster can either use the -c "crop" or -c "reflect" strategy to handle the edges since convolutions are the edges are ill-defined. *crop* removes a surrounding edge of size (n-1)/2 from the raster. "reflect" pads the array with an edge of size (n-1)/2 by "reflecting"/"mirroring" the data at the edge. The bbox is used when *reading* the raster. If the strategy is "crop" the resulting bbox will be smaller depending on the resolution and the size of the neighborhood.

#### Example
```
surfclass prepare extractfeatures -b 721000 6150000 722000 6151000 -n 5 -c reflect -f mean -f var amplitude.tif c:\outdir\
```
### `traindata`
Extracts training data from a polygon with a class column from a set of raster features. Each polygon should have a feature with the class number as an integer. The extracted training data will be an `.npz` file which is a compressed numpy save format. The number of input features given should match the features when classifying in a later step. The `.npz` file can be consumed by the `surfclass train` command to produce a trained RandomForest Model. 

#### Example
```
Example: surfclass prepare traindata --in train_polys.gpkg --inlyr areas --attrib classno -f feature1.tif -f feature2.tif -f feature3.tif my_traning_data.npz
```

### `traindatainfo`
Shows basic information about the training data prepared by `surfclass prepare traindata`. 

#### Example
```
surclass prepare traindatainfo my_traning_data.npz
```

## Train
Train contains commands for training a RandomForest model using an `.npz` file. 

`genericmodel` allows you to train a model using your preferred number of features, note that the order of the features used when generating the `.npz` file is important later when classifying.

`randomforestndvi` is a predefined model structure that takes 10 inputs f1 f2 ... f10 in correct order. Type `surfclass train randomforestndvi --help` for help. 
```
Commands:
  genericmodel      Trains a new generic model using an .npz file...
  randomforestndvi  Trains a new randomforestndvi model using an .npz file...
```
Both models let you decide the number of trees/estimators in the forest, the default is 100. More trees might increase accuracy at runtime cost. 
#### Example
```
surfclass train genericmodel -n 100 my_traning_data.npz my_randomforest.sav
```

## Classify
Creates a surface classified raster using a set of input features and a trained RandomForest model. The input features must match the model provided, the order is important. Add "-v INFO" to check that the order of the input rasters meet expectations.

```
Commands:
  genericmodel      Generic Model Create a surface classified raster using...
  randomforestndvi  RandomForestNDVI Create a surface classified raster...
```
#### Example
```
surfclass classify genericmodel -b 721000 6150000 722000 6151000
  -f 1km_6150_721_Amplitude.tif
  -f 1km_6150_721_Amplitude_mean.tif
  -f 1km_6150_721_Amplitude_var.tif
  -f 1km_6150_721_NDVI.tif
  -f 1km_6150_721_NDVI_mean.tif
  -f 1km_6150_721_NDVI_var.tif
  -f 1km_6150_721_Pulsewidth.tif
  -f 1km_6150_721_Pulsewidth_mean.tif
  -f 1km_6150_721_Pulsewidth_var.tif
  -f 1km_6171_727_ReturnNumber.tif
  --prefix surface
  --postfix my_randomforest
  my_randomforest.sav
  c:\outdir\
```
## Extract
Extract data from a surfclass classified raster. After creating a classified raster, `surfclass extract` exposes two commands `denoise` and `count`.
```
Commands:
  denoise  Applies denoising to a classified raster If bbox is specified...
  count    Count occurences of cell values inside polygons.
```
### `denoise`
Applies denoising to a classified raster. If bbox is specified only this part of the classraster will be loaded and
denoised. If bbox is not specified the entire classraster is processed. The denoise algorithm will fill out nodata values using a nearest neighbor approach.

#### Example
```
surfclass extract denoise -b 721000 6150000 722000 6151000 surface_classification_myrandomforest.tif surface_classification_myrandomforest_denoised.tif
```

### `count`
Counts the occurences of cell values inside an input polygon. This tool counts the ocurrences of specified cell values whose cell center falls inside a polygon and adds the counts as feature attributes. An attribute per reported class is added. The attribute "class_n" reports the number of cells with the value n within the polygon and a "total_count" attribute reports the total number of cells within the polygon.

#### Example
```
extract count --in inpolys.shp --out outpolys.geojson --format geojson --clip --classrange 0 5 surface_classification_myrandomforest_denoised.tif
```

# Python Module
`surfclass` can also be imported directly into exising python projects, see below for a small example for extracting derived features. 

#### Example:
```
from surfclass import Bbox
from surfclass.kernelfeatureextraction import KernelFeatureExtraction

bbox = Bbox(727000, 6171000, 728000, 6172000)
raster_filepath = "amplitude.tif"
derived_features = ["mean", "var", "diffmean"]


extractor = KernelFeatureExtraction(
    raster_filepath,
    tmp_path
    bbox=bbox,
    prefix="amplitude",
    crop_mode="crop",
)

feature_generator = extractor.calculate_derived_features()
derived_features, paths = zip(*list(feature_generator))
```
