# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterRasterDestination,
)
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
import processing


class VineyardCleanVegMaskTool(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    BAND_RED = "BAND_RED"
    BAND_NIR = "BAND_NIR"
    MSAVI2_THRESHOLD = "MSAVI2_THRESHOLD"
    SIEVE_PIXELS = "SIEVE_PIXELS"
    KEEP_MSAVI2 = "KEEP_MSAVI2"

    OUTPUT_MASK = "OUTPUT_MASK"
    OUTPUT_MSAVI2 = "OUTPUT_MSAVI2"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return VineyardCleanVegMaskTool()

    def name(self):
        return "vineyard_clean_veg_mask_tool"

    def displayName(self):
        return self.tr("Vineyard Clean Veg Mask Tool")

    def group(self):
        return self.tr("Viticulture")

    def groupId(self):
        return "viticulture"

    def shortHelpString(self):
        return self.tr(
            "Builds a clean binary vegetation mask from a multispectral raster using MSAVI2, "
            "followed by thresholding and optional sieve cleanup. "
            "Designed for early-season vineyard vegetation masking where soil background is strong."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                self.tr("Input multispectral raster")
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
            QgsProcessingParameterNumber(
                self.SIEVE_PIXELS,
                self.tr("Minimum sieve size (pixels, 0 = off)"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=8,
                minValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.KEEP_MSAVI2,
                self.tr("Also output MSAVI2 raster"),
                defaultValue=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_MASK,
                self.tr("Output clean vegetation mask")
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_MSAVI2,
                self.tr("Output MSAVI2 raster")
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

        band_red = self.parameterAsInt(parameters, self.BAND_RED, context)
        band_nir = self.parameterAsInt(parameters, self.BAND_NIR, context)
        threshold = self.parameterAsDouble(parameters, self.MSAVI2_THRESHOLD, context)
        sieve_pixels = self.parameterAsInt(parameters, self.SIEVE_PIXELS, context)
        keep_msavi2 = self.parameterAsBoolean(parameters, self.KEEP_MSAVI2, context)

        output_mask = self.parameterAsOutputLayer(parameters, self.OUTPUT_MASK, context)
        output_msavi2 = self.parameterAsOutputLayer(parameters, self.OUTPUT_MSAVI2, context)

        feedback.pushInfo("Calculating MSAVI2 raster...")
        msavi_entries = [
            self._make_entry(raster, band_red, "red@1"),
            self._make_entry(raster, band_nir, "nir@1"),
        ]
        msavi_formula = "((2 * nir@1 + 1 - sqrt(((2 * nir@1 + 1) * (2 * nir@1 + 1)) - 8 * (nir@1 - red@1))) / 2)"
        self._run_calc(msavi_formula, output_msavi2, raster, msavi_entries)

        feedback.pushInfo("Thresholding vegetation mask...")
        msavi_layer = type(raster)(output_msavi2, "msavi2")
        if not msavi_layer.isValid():
            raise QgsProcessingException("Failed to load MSAVI2 raster for mask creation.")

        mask_entries = [self._make_entry(msavi_layer, 1, "msavi@1")]
        mask_formula = f"(msavi@1 > {threshold}) * 1"
        self._run_calc(mask_formula, output_mask, msavi_layer, mask_entries)

        final_mask = output_mask
        if sieve_pixels > 0:
            feedback.pushInfo("Applying sieve cleanup...")
            sieve_tmp = output_mask.replace('.tif', '_sieved.tif') if output_mask.lower().endswith('.tif') else output_mask + '_sieved.tif'
            processing.run(
                "gdal:sieve",
                {
                    "INPUT": output_mask,
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
            final_mask = sieve_tmp

        results = {
            self.OUTPUT_MASK: final_mask,
        }

        if keep_msavi2:
            results[self.OUTPUT_MSAVI2] = output_msavi2

        return results
