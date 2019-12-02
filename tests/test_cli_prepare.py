from osgeo import gdal
from surfclass.scripts.cli import cli


def test_cli_prepare(cli_runner):
    result = cli_runner.invoke(cli, ["prepare"], catch_exceptions=False)
    assert result.exit_code == 0


def test_cli_prepare_lidargrid_help(cli_runner):
    result = cli_runner.invoke(
        cli, ["prepare", "lidargrid", "--help"], catch_exceptions=False
    )
    assert result.exit_code == 0


def test_cli_prepare_lidargrid(cli_runner, las_filepath, tmp_path):
    args = f"prepare lidargrid -b 727000 6171000 728000 6172000 -r 10 -d Z -d Intensity {las_filepath} {tmp_path}"

    result = cli_runner.invoke(cli, args.split(" "), catch_exceptions=False)
    assert result.exit_code == 0

    outfile = tmp_path / "Z.tif"
    ds = gdal.Open(str(outfile))
    assert ds.GetGeoTransform() == (727000, 10, 0, 6172000, 0, -10)
    assert ds.RasterXSize == 100
    assert ds.RasterYSize == 100
    band = ds.GetRasterBand(1)
    assert band.DataType == gdal.GDT_Float64
    ds = None

    outfile = tmp_path / "Intensity.tif"
    ds = gdal.Open(str(outfile))
    assert ds.GetGeoTransform() == (727000, 10, 0, 6172000, 0, -10)
    assert ds.RasterXSize == 100
    assert ds.RasterYSize == 100
    band = ds.GetRasterBand(1)
    assert band.DataType == gdal.GDT_UInt16
    ds = None


def test_cli_prepare_lidargrid_multiple_lidarfiles(cli_runner, las_filepath, tmp_path):
    args = f"prepare lidargrid -b 727000 6171000 728000 6172000 -r 10 -d Z -d Intensity {las_filepath} {las_filepath} {tmp_path}"

    result = cli_runner.invoke(cli, args.split(" "), catch_exceptions=False)
    assert result.exit_code == 0

    outfile = tmp_path / "Z.tif"
    ds = gdal.Open(str(outfile))
    assert ds.GetGeoTransform() == (727000, 10, 0, 6172000, 0, -10)
    assert ds.RasterXSize == 100
    assert ds.RasterYSize == 100
    band = ds.GetRasterBand(1)
    assert band.DataType == gdal.GDT_Float64
    ds = None

    outfile = tmp_path / "Intensity.tif"
    ds = gdal.Open(str(outfile))
    assert ds.GetGeoTransform() == (727000, 10, 0, 6172000, 0, -10)
    assert ds.RasterXSize == 100
    assert ds.RasterYSize == 100
    band = ds.GetRasterBand(1)
    assert band.DataType == gdal.GDT_UInt16
    ds = None


def test_cli_prepare_extractfeatures(cli_runner, amplituderaster_filepath, tmp_path):
    args = f"prepare extractfeatures -b 727000 6171000 728000 6172000 -f mean -f var -n 5 -c reflect {amplituderaster_filepath} {tmp_path}"

    result = cli_runner.invoke(cli, args.split(" "), catch_exceptions=False)
    assert result.exit_code == 0

    outfile = tmp_path / "mean.tif"
    ds = gdal.Open(str(outfile))
    assert ds.GetGeoTransform() == (727000, 4, 0, 6172000, 0, -4)
    assert ds.RasterXSize == 250
    assert ds.RasterYSize == 250
    band = ds.GetRasterBand(1)
    assert band.DataType == gdal.GDT_Float64
    ds = None

    outfile = tmp_path / "var.tif"
    ds = gdal.Open(str(outfile))
    assert ds.GetGeoTransform() == (727000, 4, 0, 6172000, 0, -4)
    assert ds.RasterXSize == 250
    assert ds.RasterYSize == 250
    band = ds.GetRasterBand(1)
    assert band.DataType == gdal.GDT_Float64
    ds = None
