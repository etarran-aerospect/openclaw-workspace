# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterDefinition,
)
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
import processing


class VineyardCleanVineMaskTool(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    ROWS = "ROWS"
    BLOCKS = "BLOCKS"

    INDEX_NAME = "INDEX_NAME"
    BAND_RED = "BAND_RED"
    BAND_REDEDGE = "BAND_REDEDGE"
    BAND_NIR = "BAND_NIR"
    BAND_GREEN = "BAND_GREEN"

    INDEX_THRESHOLD = "INDEX_THRESHOLD"
    CANOPY_WIDTH = "CANOPY_WIDTH"
    SIEVE_PIXELS = "SIEVE_PIXELS"
    CLIP_TO_BLOCK = "CLIP_TO_BLOCK"

    OUTPUT_INDEX = "OUTPUT_INDEX"
    OUTPUT_RAW_MASK = "OUTPUT_RAW_MASK"
    OUTPUT_CANOPY_MASK = "OUTPUT_CANOPY_MASK"
    OUTPUT_CLEAN_MASK = "OUTPUT_CLEAN_MASK"

    INDEX_OPTIONS = ["MSAVI2", "NDRE", "NDVI", "GNDVI"]
    EPS = 0.000001

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return VineyardCleanVineMaskTool()

    def name(self):
        return "vineyard_clean_vine_mask_tool"

    def displayName(self):
        return self.tr("Vineyard Clean Vine Mask Tool")

    def group(self):
        return self.tr("Viticulture")

    def groupId(self):
        return "viticulture"

    def shortHelpString(self):
        return self.tr(
            "Builds a cleaner binary vine mask from multispectral imagery by combining a vegetation index threshold with row geometry. "
            "Workflow: calculate vegetation index, threshold to raw vegetation mask, build row canopy corridor from full canopy width, rasterize corridor, intersect corridor with vegetation mask, then sieve the result."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_RASTER, self.tr("Input multispectral raster")))
        self.addParameter(QgsProcessingParameterFeatureSource(self.ROWS, self.tr("Row centerlines"), [QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.BLOCKS, self.tr("Block polygon"), [QgsProcessing.TypeVectorPolygon]))

        self.addParameter(QgsProcessingParameterEnum(self.INDEX_NAME, self.tr("Vegetation index"), options=self.INDEX_OPTIONS, defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.BAND_GREEN, self.tr("Green band number"), type=QgsProcessingParameterNumber.Integer, defaultValue=2, minValue=1))
        self.addParameter(QgsProcessingParameterNumber(self.BAND_RED, self.tr("Red band number"), type=QgsProcessingParameterNumber.Integer, defaultValue=3, minValue=1))
        self.addParameter(QgsProcessingParameterNumber(self.BAND_REDEDGE, self.tr("Red-edge band number"), type=QgsProcessingParameterNumber.Integer, defaultValue=5, minValue=1))
        self.addParameter(QgsProcessingParameterNumber(self.BAND_NIR, self.tr("NIR band number"), type=QgsProcessingParameterNumber.Integer, defaultValue=4, minValue=1))

        self.addParameter(QgsProcessingParameterNumber(self.INDEX_THRESHOLD, self.tr("Index threshold (index > threshold = vegetation)"), type=QgsProcessingParameterNumber.Double, defaultValue=0.30))
        self.addParameter(QgsProcessingParameterNumber(self.CANOPY_WIDTH, self.tr("Full canopy width (m)"), type=QgsProcessingParameterNumber.Double, defaultValue=3.35, minValue=0.01))
        self.addParameter(QgsProcessingParameterNumber(self.SIEVE_PIXELS, self.tr("Minimum sieve size (pixels)"), type=QgsProcessingParameterNumber.Integer, defaultValue=8, minValue=0))

        clip_param = QgsProcessingParameterBoolean(self.CLIP_TO_BLOCK, self.tr("Clip canopy corridor to block before rasterizing"), defaultValue=True)
        clip_param.setFlags(clip_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(clip_param)

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_INDEX, self.tr("Output vegetation index raster")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_RAW_MASK, self.tr("Output raw vegetation mask")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_CANOPY_MASK, self.tr("Output canopy corridor mask")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_CLEAN_MASK, self.tr("Output clean vine mask")))

    def _make_entry(self, raster, band_number, ref):
        entry = QgsRasterCalculatorEntry()
        entry.ref = ref
        entry.raster = raster
        entry.bandNumber = band_number
        return entry

    def _run_calc(self, formula, output_path, base_raster, entries):
        calc = QgsRasterCalculator(
            formula,
            output_path,
            "GTiff",
            base_raster.extent(),
            base_raster.width(),
            base_raster.height(),
            entries,
        )
        result = calc.processCalculation()
        if result != 0:
            raise QgsProcessingException(f"Raster calculation failed for {output_path}. Code: {result}")

    def processAlgorithm(self, parameters, context, feedback):
        raster = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        if raster is None:
            raise QgsProcessingException("Input raster is invalid.")

        index_name = self.INDEX_OPTIONS[self.parameterAsEnum(parameters, self.INDEX_NAME, context)]
        band_green = self.parameterAsInt(parameters, self.BAND_GREEN, context)
        band_red = self.parameterAsInt(parameters, self.BAND_RED, context)
        band_rededge = self.parameterAsInt(parameters, self.BAND_REDEDGE, context)
        band_nir = self.parameterAsInt(parameters, self.BAND_NIR, context)
        index_threshold = self.parameterAsDouble(parameters, self.INDEX_THRESHOLD, context)
        canopy_width = self.parameterAsDouble(parameters, self.CANOPY_WIDTH, context)
        sieve_pixels = self.parameterAsInt(parameters, self.SIEVE_PIXELS, context)
        clip_to_block = self.parameterAsBoolean(parameters, self.CLIP_TO_BLOCK, context)

        output_index = self.parameterAsOutputLayer(parameters, self.OUTPUT_INDEX, context)
        output_raw_mask = self.parameterAsOutputLayer(parameters, self.OUTPUT_RAW_MASK, context)
        output_canopy_mask = self.parameterAsOutputLayer(parameters, self.OUTPUT_CANOPY_MASK, context)
        output_clean_mask = self.parameterAsOutputLayer(parameters, self.OUTPUT_CLEAN_MASK, context)

        entries = [
            self._make_entry(raster, band_green, "green@1"),
            self._make_entry(raster, band_red, "red@1"),
            self._make_entry(raster, band_rededge, "re@1"),
            self._make_entry(raster, band_nir, "nir@1"),
        ]

        if index_name == "MSAVI2":
            formula = "((2 * nir@1 + 1 - sqrt(((2 * nir@1 + 1) * (2 * nir@1 + 1)) - 8 * (nir@1 - red@1))) / 2)"
        elif index_name == "NDRE":
            formula = f"((nir@1 - re@1) / ((nir@1 + re@1) + {self.EPS}))"
        elif index_name == "NDVI":
            formula = f"((nir@1 - red@1) / ((nir@1 + red@1) + {self.EPS}))"
        elif index_name == "GNDVI":
            formula = f"((nir@1 - green@1) / ((nir@1 + green@1) + {self.EPS}))"
        else:
            raise QgsProcessingException(f"Unsupported index: {index_name}")

        feedback.pushInfo(f"Calculating {index_name} raster...")
        self._run_calc(formula, output_index, raster, entries)

        feedback.pushInfo("Thresholding raw vegetation mask...")
        idx_layer = type(raster)(output_index, f"{index_name}_index")
        if not idx_layer.isValid():
            raise QgsProcessingException("Failed to load index raster for raw mask creation.")

        mask_entries = [self._make_entry(idx_layer, 1, "idx@1")]
        raw_mask_formula = f"(idx@1 > {index_threshold}) * 1"
        self._run_calc(raw_mask_formula, output_raw_mask, idx_layer, mask_entries)

        feedback.pushInfo("Buffering rows to build canopy corridor...")
        canopy_half_width = canopy_width / 2.0
        canopy_result = processing.run(
            "native:buffer",
            {
                "INPUT": parameters[self.ROWS],
                "DISTANCE": canopy_half_width,
                "SEGMENTS": 8,
                "END_CAP_STYLE": 0,
                "JOIN_STYLE": 0,
                "MITER_LIMIT": 2,
                "DISSOLVE": True,
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
        )
        canopy = canopy_result["OUTPUT"]

        if clip_to_block:
            feedback.pushInfo("Clipping canopy corridor to block...")
            clip_result = processing.run(
                "native:clip",
                {
                    "INPUT": canopy,
                    "OVERLAY": parameters[self.BLOCKS],
                    "OUTPUT": "memory:",
                },
                context=context,
                feedback=feedback,
            )
            canopy = clip_result["OUTPUT"]

        feedback.pushInfo("Rasterizing canopy corridor...")
        extent = raster.extent()
        crs_authid = raster.crs().authid()
        pixel_size_x = raster.rasterUnitsPerPixelX()
        pixel_size_y = raster.rasterUnitsPerPixelY()

        processing.run(
            "gdal:rasterize",
            {
                "INPUT": canopy,
                "FIELD": None,
                "BURN": 1,
                "USE_Z": False,
                "UNITS": 1,
                "WIDTH": abs(pixel_size_x),
                "HEIGHT": abs(pixel_size_y),
                "EXTENT": f"{extent.xMinimum()},{extent.xMaximum()},{extent.yMinimum()},{extent.yMaximum()} [{crs_authid}]",
                "NODATA": 0,
                "OPTIONS": "",
                "DATA_TYPE": 5,
                "INIT": 0,
                "INVERT": False,
                "EXTRA": "",
                "OUTPUT": output_canopy_mask,
            },
            context=context,
            feedback=feedback,
        )

        feedback.pushInfo("Combining raw vegetation mask with canopy corridor mask...")
        raw_mask_layer = type(raster)(output_raw_mask, "raw_mask")
        canopy_mask_layer = type(raster)(output_canopy_mask, "canopy_mask")
        if not raw_mask_layer.isValid() or not canopy_mask_layer.isValid():
            raise QgsProcessingException("Failed to load raw or canopy mask rasters for clean mask creation.")

        clean_entries = [
            self._make_entry(raw_mask_layer, 1, "raw@1"),
            self._make_entry(canopy_mask_layer, 1, "canopy@1"),
        ]
        clean_formula = "((raw@1 = 1) AND (canopy@1 = 1)) * 1"
        self._run_calc(clean_formula, output_clean_mask, raw_mask_layer, clean_entries)

        if sieve_pixels > 0:
            feedback.pushInfo("Applying sieve cleanup to clean vine mask...")
            sieve_tmp = output_clean_mask.replace('.tif', '_sieved.tif') if output_clean_mask.lower().endswith('.tif') else output_clean_mask + '_sieved.tif'
            processing.run(
                "gdal:sieve",
                {
                    "INPUT": output_clean_mask,
                    "THRESHOLD": sieve_pixels,
                    "EIGHT_CONNECTEDNESS": False,
                    "NO_MASK": True,
                    "MASK_LAYER": None,
                    "EXTRA": "",
                    "OUTPUT": sieve_tmp,
                },
                context=context,
                feedback=feedback,
            )
            output_clean_mask = sieve_tmp

        return {
            self.OUTPUT_INDEX: output_index,
            self.OUTPUT_RAW_MASK: output_raw_mask,
            self.OUTPUT_CANOPY_MASK: output_canopy_mask,
            self.OUTPUT_CLEAN_MASK: output_clean_mask,
        }
