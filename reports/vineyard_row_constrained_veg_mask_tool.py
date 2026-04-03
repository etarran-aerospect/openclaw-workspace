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
    QgsProcessingParameterRasterDestination,
)
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
import processing


class VineyardRowConstrainedVegMaskTool(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    ROWS = "ROWS"
    ROW_INPUT_TYPE = "ROW_INPUT_TYPE"
    CANOPY_WIDTH = "CANOPY_WIDTH"

    BAND_RED = "BAND_RED"
    BAND_NIR = "BAND_NIR"
    MSAVI2_THRESHOLD = "MSAVI2_THRESHOLD"

    OUTPUT_MASK = "OUTPUT_MASK"

    ROW_INPUT_OPTIONS = ["Centerlines (buffer internally)", "Buffered canopy polygons (use directly)"]

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return VineyardRowConstrainedVegMaskTool()

    def name(self):
        return "vineyard_row_constrained_veg_mask_tool"

    def displayName(self):
        return self.tr("Vineyard Row-Constrained Veg Mask Tool")

    def group(self):
        return self.tr("Viticulture")

    def groupId(self):
        return "viticulture"

    def shortHelpString(self):
        return self.tr(
            "Builds a clean vineyard vegetation mask by combining a multispectral MSAVI2 threshold with row geometry. "
            "Use row centerlines with canopy width or prebuffered canopy polygons to remove interrow vegetation from the mask."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                self.tr("Input multispectral raster")
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ROWS,
                self.tr("Rows (centerlines or buffered canopy polygons)"),
                [QgsProcessing.TypeVectorLine, QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.ROW_INPUT_TYPE,
                self.tr("Row input type"),
                options=self.ROW_INPUT_OPTIONS,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.CANOPY_WIDTH,
                self.tr("Full canopy width (m, used only for centerlines)"),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=3.35,
                minValue=0.01,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.BAND_RED,
                self.tr("Red band number"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=3,
                minValue=1,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.BAND_NIR,
                self.tr("NIR band number"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=4,
                minValue=1,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MSAVI2_THRESHOLD,
                self.tr("MSAVI2 threshold (MSAVI2 > threshold = vegetation)"),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.30,
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_MASK,
                self.tr("Output clean vineyard vegetation mask")
            )
        )

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

        row_input_type = self.parameterAsEnum(parameters, self.ROW_INPUT_TYPE, context)
        canopy_width = self.parameterAsDouble(parameters, self.CANOPY_WIDTH, context)
        band_red = self.parameterAsInt(parameters, self.BAND_RED, context)
        band_nir = self.parameterAsInt(parameters, self.BAND_NIR, context)
        threshold = self.parameterAsDouble(parameters, self.MSAVI2_THRESHOLD, context)
        output_mask = self.parameterAsOutputLayer(parameters, self.OUTPUT_MASK, context)

        feedback.pushInfo("Calculating MSAVI2 raster...")
        msavi_tmp = output_mask.replace('.tif', '_msavi2_tmp.tif') if output_mask.lower().endswith('.tif') else output_mask + '_msavi2_tmp.tif'
        msavi_entries = [
            self._make_entry(raster, band_red, "red@1"),
            self._make_entry(raster, band_nir, "nir@1"),
        ]
        msavi_formula = "((2 * nir@1 + 1 - sqrt(((2 * nir@1 + 1) * (2 * nir@1 + 1)) - 8 * (nir@1 - red@1))) / 2)"
        self._run_calc(msavi_formula, msavi_tmp, raster, msavi_entries)

        feedback.pushInfo("Building raw vegetation mask...")
        raw_mask_tmp = output_mask.replace('.tif', '_raw_mask_tmp.tif') if output_mask.lower().endswith('.tif') else output_mask + '_raw_mask_tmp.tif'
        msavi_layer = type(raster)(msavi_tmp, "msavi2")
        if not msavi_layer.isValid():
            raise QgsProcessingException("Failed to load MSAVI2 raster.")

        raw_entries = [self._make_entry(msavi_layer, 1, "msavi@1")]
        raw_formula = f"(msavi@1 > {threshold}) * 1"
        self._run_calc(raw_formula, raw_mask_tmp, msavi_layer, raw_entries)

        if row_input_type == 0:
            feedback.pushInfo("Buffering row centerlines to canopy width...")
            canopy_half_width = canopy_width / 2.0
            row_zone_result = processing.run(
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
            row_zone = row_zone_result["OUTPUT"]
        else:
            feedback.pushInfo("Using buffered canopy polygons directly...")
            dissolve_result = processing.run(
                "native:dissolve",
                {
                    "INPUT": parameters[self.ROWS],
                    "FIELD": [],
                    "SEPARATE_DISJOINT": False,
                    "OUTPUT": "memory:",
                },
                context=context,
                feedback=feedback,
            )
            row_zone = dissolve_result["OUTPUT"]

        feedback.pushInfo("Rasterizing row zone...")
        row_zone_tmp = output_mask.replace('.tif', '_row_zone_tmp.tif') if output_mask.lower().endswith('.tif') else output_mask + '_row_zone_tmp.tif'
        extent = raster.extent()
        crs_authid = raster.crs().authid()
        pixel_size_x = raster.rasterUnitsPerPixelX()
        pixel_size_y = raster.rasterUnitsPerPixelY()

        processing.run(
            "gdal:rasterize",
            {
                "INPUT": row_zone,
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
                "OUTPUT": row_zone_tmp,
            },
            context=context,
            feedback=feedback,
        )

        feedback.pushInfo("Applying row constraint to vegetation mask...")
        raw_mask_layer = type(raster)(raw_mask_tmp, "raw_mask")
        row_zone_layer = type(raster)(row_zone_tmp, "row_zone")
        if not raw_mask_layer.isValid() or not row_zone_layer.isValid():
            raise QgsProcessingException("Failed to load raw mask or row zone raster.")

        final_entries = [
            self._make_entry(raw_mask_layer, 1, "raw@1"),
            self._make_entry(row_zone_layer, 1, "row@1"),
        ]
        final_formula = "((raw@1 = 1) AND (row@1 = 1)) * 1"
        self._run_calc(final_formula, output_mask, raw_mask_layer, final_entries)

        return {
            self.OUTPUT_MASK: output_mask,
        }
