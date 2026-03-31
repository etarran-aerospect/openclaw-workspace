# -*- coding: utf-8 -*-

"""
Vineyard Row Builder Production (Canonical)
QGIS Processing Toolbox script

Purpose
-------
Build vineyard row centerlines from a single manually drawn reference row.

Design principles
-----------------
- The reference row geometry controls row direction and shape.
- The block polygon does NOT guide row direction or geometry.
- The block polygon is used only to:
  - retain relevant rows by intersection length
  - optionally clip final output for display/export
- The tool is intended for projected CRS / meter-based workflows.

Recommended use
---------------
- Use one carefully drawn reference row centerline.
- Use projected CRS with linear units in meters.
- Keep output unclipped for analysis.
- Use clipping only for export or cartographic display.
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterDefinition,
    QgsFeature,
    QgsFields,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsWkbTypes,
    QgsFeatureSink,
    QgsVectorLayer,
    QgsUnitTypes,
)
import processing
import math


class VineyardRowBuilderProductionCanonical(QgsProcessingAlgorithm):
    BLOCKS = "BLOCKS"
    REF_ROW = "REF_ROW"
    VEG_MASK = "VEG_MASK"

    USE_MASK = "USE_MASK"
    CLIP_OUTPUT_TO_BLOCK = "CLIP_OUTPUT_TO_BLOCK"
    SMOOTH_REFERENCE = "SMOOTH_REFERENCE"

    ROW_SPACING = "ROW_SPACING"
    ROWS_EACH_SIDE = "ROWS_EACH_SIDE"
    MIN_ROW_LENGTH = "MIN_ROW_LENGTH"
    MIN_BLOCK_INTERSECTION = "MIN_BLOCK_INTERSECTION"
    MIN_MASK_INTERSECTION = "MIN_MASK_INTERSECTION"
    SMOOTH_ITERATIONS = "SMOOTH_ITERATIONS"

    OUTPUT_ROWS = "OUTPUT_ROWS"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return VineyardRowBuilderProductionCanonical()

    def name(self):
        return "vineyard_row_builder_production_canonical"

    def displayName(self):
        return self.tr("Vineyard Row Builder Production (Canonical)")

    def group(self):
        return self.tr("Viticulture")

    def groupId(self):
        return "viticulture"

    def shortHelpString(self):
        return self.tr(
            "Builds vineyard row centerlines from one reference row. "
            "The reference row geometry controls row direction and shape; the block polygon does not guide geometry. "
            "The block is used only to retain relevant rows and optionally clip final output.\n\n"
            "Recommended practice:\n"
            "- Use a carefully drawn reference row centerline\n"
            "- Use projected CRS in meters\n"
            "- Keep CLIP_OUTPUT_TO_BLOCK = False during analysis\n"
            "- Turn clipping on only for export or display"
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.BLOCKS,
                self.tr("Vineyard block polygon"),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.REF_ROW,
                self.tr("Reference row line (exactly one line feature)"),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SMOOTH_REFERENCE,
                self.tr("Smooth reference row before offsetting"),
                defaultValue=False
            )
        )

        smooth_iter_param = QgsProcessingParameterNumber(
            self.SMOOTH_ITERATIONS,
            self.tr("Reference smoothing iterations"),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=1,
            minValue=1
        )
        smooth_iter_param.setFlags(smooth_iter_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(smooth_iter_param)

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_MASK,
                self.tr("Use vegetation mask to filter candidate rows"),
                defaultValue=False
            )
        )

        mask_param = QgsProcessingParameterRasterLayer(
            self.VEG_MASK,
            self.tr("Vegetation mask raster (1 vegetation, 0 background)"),
            optional=True
        )
        mask_param.setFlags(mask_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(mask_param)

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CLIP_OUTPUT_TO_BLOCK,
                self.tr("Clip output rows to block polygon"),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ROW_SPACING,
                self.tr("Row spacing (m)"),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=3.2,
                minValue=0.1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ROWS_EACH_SIDE,
                self.tr("Number of rows to generate on each side of reference row"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=80,
                minValue=1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MIN_ROW_LENGTH,
                self.tr("Minimum retained row length (m)"),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                minValue=0.0
            )
        )

        min_block_param = QgsProcessingParameterNumber(
            self.MIN_BLOCK_INTERSECTION,
            self.tr("Minimum length intersecting block polygon (m)"),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=10.0,
            minValue=0.0
        )
        min_block_param.setFlags(min_block_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(min_block_param)

        min_mask_param = QgsProcessingParameterNumber(
            self.MIN_MASK_INTERSECTION,
            self.tr("Minimum length intersecting vegetation mask (m)"),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=5.0,
            minValue=0.0
        )
        min_mask_param.setFlags(min_mask_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(min_mask_param)

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_ROWS,
                self.tr("Output row centerlines")
            )
        )

    def _merge_block_geometry(self, block_features):
        merged = None
        for f in block_features:
            g = f.geometry()
            if g is None or g.isEmpty():
                continue
            if merged is None:
                merged = QgsGeometry(g)
            else:
                merged = merged.combine(g)
        return merged

    def _extract_reference_polyline(self, geom):
        if geom is None or geom.isEmpty():
            raise QgsProcessingException("Reference row geometry is empty.")

        line = geom.asPolyline()
        if len(line) >= 2:
            return line

        multi = geom.asMultiPolyline()
        if multi and len(multi[0]) >= 2:
            return multi[0]

        raise QgsProcessingException("Reference row must contain at least two vertices.")

    def _smooth_line(self, line_pts, iterations=1):
        if len(line_pts) < 3:
            return line_pts[:]

        pts = line_pts[:]
        for _ in range(iterations):
            if len(pts) < 3:
                break
            smoothed = [pts[0]]
            for i in range(len(pts) - 1):
                p = pts[i]
                q = pts[i + 1]
                q1 = QgsPointXY(0.75 * p.x() + 0.25 * q.x(), 0.75 * p.y() + 0.25 * q.y())
                q2 = QgsPointXY(0.25 * p.x() + 0.75 * q.x(), 0.25 * p.y() + 0.75 * q.y())
                if i == 0:
                    smoothed.append(q2)
                elif i == len(pts) - 2:
                    smoothed.append(q1)
                else:
                    smoothed.append(q1)
                    smoothed.append(q2)
            smoothed.append(pts[-1])
            pts = smoothed
        return pts

    def _check_crs_linear(self, source, feedback):
        crs = source.sourceCrs()
        units = crs.mapUnits()
        if units == QgsUnitTypes.DistanceDegrees:
            raise QgsProcessingException(
                "This tool requires a projected CRS with linear units (meters/feet), not geographic degrees. "
                "Reproject your data before running the tool."
            )
        if units != QgsUnitTypes.DistanceMeters:
            feedback.pushInfo(
                f"Warning: CRS map units are not meters ({QgsUnitTypes.toString(units)}). "
                "The tool will still run, but row spacing and lengths will be interpreted in CRS units."
            )

    def processAlgorithm(self, parameters, context, feedback):
        blocks = self.parameterAsSource(parameters, self.BLOCKS, context)
        ref_rows = self.parameterAsSource(parameters, self.REF_ROW, context)
        use_mask = self.parameterAsBoolean(parameters, self.USE_MASK, context)
        veg_mask = self.parameterAsRasterLayer(parameters, self.VEG_MASK, context)
        clip_output = self.parameterAsBoolean(parameters, self.CLIP_OUTPUT_TO_BLOCK, context)
        smooth_reference = self.parameterAsBoolean(parameters, self.SMOOTH_REFERENCE, context)

        row_spacing = self.parameterAsDouble(parameters, self.ROW_SPACING, context)
        rows_each_side = self.parameterAsInt(parameters, self.ROWS_EACH_SIDE, context)
        min_row_length = self.parameterAsDouble(parameters, self.MIN_ROW_LENGTH, context)
        min_block_intersection = self.parameterAsDouble(parameters, self.MIN_BLOCK_INTERSECTION, context)
        min_mask_intersection = self.parameterAsDouble(parameters, self.MIN_MASK_INTERSECTION, context)
        smooth_iterations = self.parameterAsInt(parameters, self.SMOOTH_ITERATIONS, context)

        if blocks is None:
            raise QgsProcessingException("Block polygon layer is invalid.")
        if ref_rows is None:
            raise QgsProcessingException("Reference row layer is invalid.")
        if use_mask and veg_mask is None:
            raise QgsProcessingException("Use vegetation mask is checked, but no vegetation mask raster was provided.")

        self._check_crs_linear(blocks, feedback)
        self._check_crs_linear(ref_rows, feedback)

        block_features = list(blocks.getFeatures())
        if not block_features:
            raise QgsProcessingException("No block polygons found.")

        merged_block = self._merge_block_geometry(block_features)
        if merged_block is None or merged_block.isEmpty():
            raise QgsProcessingException("Merged block geometry is empty.")

        ref_features = list(ref_rows.getFeatures())
        if len(ref_features) != 1:
            raise QgsProcessingException("Reference row layer must contain exactly one line feature.")

        ref_geom = ref_features[0].geometry()
        ref_line = self._extract_reference_polyline(ref_geom)

        if smooth_reference:
            feedback.pushInfo(f"Smoothing reference row with {smooth_iterations} iteration(s)...")
            ref_line = self._smooth_line(ref_line, smooth_iterations)

        if len(ref_line) < 2:
            raise QgsProcessingException("Reference row is invalid after smoothing.")

        p1 = ref_line[0]
        p2 = ref_line[-1]

        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = math.hypot(dx, dy)
        if length == 0:
            raise QgsProcessingException("Reference row has zero length.")

        ux = dx / length
        uy = dy / length
        px = -uy
        py = ux

        crs_authid = blocks.sourceCrs().authid()
        mem_lines = QgsVectorLayer(f"LineString?crs={crs_authid}", "candidate_rows", "memory")
        dp = mem_lines.dataProvider()
        dp.addAttributes([
            QgsField("cand_id", QVariant.Int),
            QgsField("offset_m", QVariant.Double)
        ])
        mem_lines.updateFields()

        feedback.pushInfo("Generating candidate rows from reference row geometry...")
        cand_feats = []
        cand_id = 1

        for i in range(-rows_each_side, rows_each_side + 1):
            offset = i * row_spacing
            shifted_pts = [
                QgsPointXY(pt.x() + offset * px, pt.y() + offset * py)
                for pt in ref_line
            ]

            feat = QgsFeature(mem_lines.fields())
            feat.setGeometry(QgsGeometry.fromPolylineXY(shifted_pts))
            feat["cand_id"] = cand_id
            feat["offset_m"] = float(offset)
            cand_feats.append(feat)
            cand_id += 1

        dp.addFeatures(cand_feats)
        mem_lines.updateExtents()

        exploded = processing.run(
            "native:multiparttosingleparts",
            {
                "INPUT": mem_lines,
                "OUTPUT": "memory:"
            },
            context=context,
            feedback=feedback
        )["OUTPUT"]

        feedback.pushInfo("Measuring block intersection per candidate row...")
        block_len_by_id = {}

        block_intersections = processing.run(
            "native:intersection",
            {
                "INPUT": exploded,
                "OVERLAY": parameters[self.BLOCKS],
                "INPUT_FIELDS": ["cand_id", "offset_m"],
                "OVERLAY_FIELDS": [],
                "OVERLAY_FIELDS_PREFIX": "",
                "OUTPUT": "memory:"
            },
            context=context,
            feedback=feedback
        )["OUTPUT"]

        for bf in block_intersections.getFeatures():
            cid = bf["cand_id"]
            geom = bf.geometry()
            seg_len = geom.length() if geom and not geom.isEmpty() else 0.0
            block_len_by_id[cid] = block_len_by_id.get(cid, 0.0) + seg_len

        mask_len_by_id = {}
        if use_mask:
            feedback.pushInfo("Polygonizing vegetation mask...")
            veg_polys = processing.run(
                "gdal:polygonize",
                {
                    "INPUT": parameters[self.VEG_MASK],
                    "BAND": 1,
                    "FIELD": "DN",
                    "EIGHT_CONNECTEDNESS": False,
                    "EXTRA": "",
                    "OUTPUT": "memory:"
                },
                context=context,
                feedback=feedback
            )["OUTPUT"]

            feedback.pushInfo("Extracting mask polygons where DN=1...")
            veg_only = processing.run(
                "native:extractbyexpression",
                {
                    "INPUT": veg_polys,
                    "EXPRESSION": '"DN" = 1',
                    "OUTPUT": "memory:"
                },
                context=context,
                feedback=feedback
            )["OUTPUT"]

            feedback.pushInfo("Measuring vegetation-mask intersection per candidate row...")
            row_mask_intersections = processing.run(
                "native:intersection",
                {
                    "INPUT": exploded,
                    "OVERLAY": veg_only,
                    "INPUT_FIELDS": ["cand_id", "offset_m"],
                    "OVERLAY_FIELDS": [],
                    "OVERLAY_FIELDS_PREFIX": "",
                    "OUTPUT": "memory:"
                },
                context=context,
                feedback=feedback
            )["OUTPUT"]

            for mf in row_mask_intersections.getFeatures():
                cid = mf["cand_id"]
                geom = mf.geometry()
                seg_len = geom.length() if geom and not geom.isEmpty() else 0.0
                mask_len_by_id[cid] = mask_len_by_id.get(cid, 0.0) + seg_len

        kept_rows = QgsVectorLayer(f"LineString?crs={crs_authid}", "kept_rows", "memory")
        kept_dp = kept_rows.dataProvider()

        out_fields = QgsFields()
        out_fields.append(QgsField("row_id", QVariant.Int))
        out_fields.append(QgsField("cand_id", QVariant.Int))
        out_fields.append(QgsField("offset_m", QVariant.Double))
        out_fields.append(QgsField("row_len_m", QVariant.Double))
        out_fields.append(QgsField("blk_len_m", QVariant.Double))
        out_fields.append(QgsField("mask_len_m", QVariant.Double))

        kept_dp.addAttributes(out_fields)
        kept_rows.updateFields()

        feedback.pushInfo("Filtering accepted rows...")
        kept_feats = []
        row_num = 1

        for f in exploded.getFeatures():
            geom = f.geometry()
            if geom is None or geom.isEmpty():
                continue

            full_len = geom.length()
            if full_len < min_row_length:
                continue

            cid = f["cand_id"]
            block_len = block_len_by_id.get(cid, 0.0)
            mask_len = mask_len_by_id.get(cid, 0.0)

            if block_len < min_block_intersection:
                continue

            if use_mask and mask_len < min_mask_intersection:
                continue

            out_feat = QgsFeature(kept_rows.fields())
            out_feat.setGeometry(geom)
            out_feat["row_id"] = row_num
            out_feat["cand_id"] = int(cid)
            out_feat["offset_m"] = float(f["offset_m"])
            out_feat["row_len_m"] = float(full_len)
            out_feat["blk_len_m"] = float(block_len)
            out_feat["mask_len_m"] = float(mask_len)
            kept_feats.append(out_feat)
            row_num += 1

        if not kept_feats:
            raise QgsProcessingException(
                "No rows were kept. Check reference row, row spacing, number of offsets, "
                "minimum block intersection, and mask settings."
            )

        kept_dp.addFeatures(kept_feats)
        kept_rows.updateExtents()

        final_layer = kept_rows

        if clip_output:
            feedback.pushInfo("Clipping final output rows to block polygon...")
            final_layer = processing.run(
                "native:clip",
                {
                    "INPUT": kept_rows,
                    "OVERLAY": parameters[self.BLOCKS],
                    "OUTPUT": "memory:"
                },
                context=context,
                feedback=feedback
            )["OUTPUT"]

            final_layer = processing.run(
                "native:multiparttosingleparts",
                {
                    "INPUT": final_layer,
                    "OUTPUT": "memory:"
                },
                context=context,
                feedback=feedback
            )["OUTPUT"]

        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT_ROWS,
            context,
            out_fields,
            QgsWkbTypes.LineString,
            blocks.sourceCrs()
        )

        feedback.pushInfo("Writing output rows...")
        for f in final_layer.getFeatures():
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        return {
            self.OUTPUT_ROWS: dest_id
        }
