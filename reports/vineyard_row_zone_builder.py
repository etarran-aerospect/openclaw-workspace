# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsWkbTypes,
)
import processing


class VineyardRowZoneBuilder(QgsProcessingAlgorithm):
    ROWS = "ROWS"
    BLOCKS = "BLOCKS"
    CANOPY_HALF_WIDTH = "CANOPY_HALF_WIDTH"
    INTERROW_INSET = "INTERROW_INSET"
    DISSOLVE_CANOPY = "DISSOLVE_CANOPY"

    OUTPUT_CANOPY = "OUTPUT_CANOPY"
    OUTPUT_INTERROW = "OUTPUT_INTERROW"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return VineyardRowZoneBuilder()

    def name(self):
        return "vineyard_row_zone_builder"

    def displayName(self):
        return self.tr("Vineyard Row Zone Builder")

    def group(self):
        return self.tr("Viticulture")

    def groupId(self):
        return "viticulture"

    def shortHelpString(self):
        return self.tr(
            "Builds vineyard row canopy-corridor and interrow-zone polygons from row centerlines and a block polygon. "
            "Useful for refining vine masks, defining cleaner non-vine analysis zones, and creating explanatory demo layers."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ROWS,
                self.tr("Row centerlines"),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.BLOCKS,
                self.tr("Block polygon"),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.CANOPY_HALF_WIDTH,
                self.tr("Canopy corridor half-width (m)"),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.5,
                minValue=0.01
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.INTERROW_INSET,
                self.tr("Optional interrow inset/erosion distance (m)"),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.0,
                minValue=0.0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISSOLVE_CANOPY,
                self.tr("Dissolve canopy corridor output (1 yes, 0 no)"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1,
                minValue=0,
                maxValue=1
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_CANOPY,
                self.tr("Output canopy corridor polygons")
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_INTERROW,
                self.tr("Output interrow polygons")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        canopy_half_width = self.parameterAsDouble(parameters, self.CANOPY_HALF_WIDTH, context)
        interrow_inset = self.parameterAsDouble(parameters, self.INTERROW_INSET, context)
        dissolve_canopy = self.parameterAsInt(parameters, self.DISSOLVE_CANOPY, context)

        feedback.pushInfo("Buffering rows to create canopy corridor...")
        canopy_result = processing.run(
            "native:buffer",
            {
                "INPUT": parameters[self.ROWS],
                "DISTANCE": canopy_half_width,
                "SEGMENTS": 8,
                "END_CAP_STYLE": 0,
                "JOIN_STYLE": 0,
                "MITER_LIMIT": 2,
                "DISSOLVE": bool(dissolve_canopy),
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
        )
        canopy = canopy_result["OUTPUT"]

        feedback.pushInfo("Clipping canopy corridor to block...")
        canopy_clip_result = processing.run(
            "native:clip",
            {
                "INPUT": canopy,
                "OVERLAY": parameters[self.BLOCKS],
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
        )
        canopy_clip = canopy_clip_result["OUTPUT"]

        feedback.pushInfo("Building interrow zone from block minus canopy corridor...")
        interrow_result = processing.run(
            "native:difference",
            {
                "INPUT": parameters[self.BLOCKS],
                "OVERLAY": canopy_clip,
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
        )
        interrow = interrow_result["OUTPUT"]

        if interrow_inset > 0:
            feedback.pushInfo("Applying optional interrow inset...")
            inset_result = processing.run(
                "native:buffer",
                {
                    "INPUT": interrow,
                    "DISTANCE": -interrow_inset,
                    "SEGMENTS": 8,
                    "END_CAP_STYLE": 0,
                    "JOIN_STYLE": 0,
                    "MITER_LIMIT": 2,
                    "DISSOLVE": False,
                    "OUTPUT": "memory:",
                },
                context=context,
                feedback=feedback,
            )
            interrow = inset_result["OUTPUT"]

        canopy_sink, canopy_dest = self.parameterAsSink(
            parameters,
            self.OUTPUT_CANOPY,
            context,
            canopy_clip.fields(),
            QgsWkbTypes.Polygon,
            self.parameterAsSource(parameters, self.BLOCKS, context).sourceCrs(),
        )

        for f in canopy_clip.getFeatures():
            canopy_sink.addFeature(f)

        interrow_sink, interrow_dest = self.parameterAsSink(
            parameters,
            self.OUTPUT_INTERROW,
            context,
            interrow.fields(),
            QgsWkbTypes.Polygon,
            self.parameterAsSource(parameters, self.BLOCKS, context).sourceCrs(),
        )

        for f in interrow.getFeatures():
            interrow_sink.addFeature(f)

        return {
            self.OUTPUT_CANOPY: canopy_dest,
            self.OUTPUT_INTERROW: interrow_dest,
        }
